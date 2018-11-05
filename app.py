from flask import Flask, jsonify, current_app, abort, request, render_template, Response
from graphql_server import (HttpQueryError, default_format_error,
                            encode_execution_results, json_encode,
                            load_json_body, run_http_query)
from functools import wraps, partial

from crossdomain import crossdomain

from schema import schema

from authorisation import AuthorisationError, requestHandler
from users import AuthError, resolve
from mongo import getClient


app = Flask(__name__)
app.config.from_envvar('CYBERPLANNING_SETTINGS')


@app.route('/graphql/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@crossdomain(origin='*', methods=['GET', 'POST'])
def graphql():
    request_method = request.method.lower()
    if request_method == 'get':
        return render_template(
            'graphiql.html',
            graphiql_version="0.11.11",
            graphiql_html_title="Cyber GraphiQL",
        )
    
    token = requestHandler(request)

    try:
        data = load_json_body(request.data.decode('utf8'))

        pretty = request.args.get('pretty')
        context = {
            'token': token
        }

        execution_results, _ = run_http_query(
            schema,
            request_method,
            data,
            query_data=request.args,
            batch_enabled=False,
            catch=False,
            backend=None,

            # Execute options
            root=None,
            context=context,
            middleware=None,
        )
        result, status_code = encode_execution_results(
            execution_results,
            is_batch=False,
            format_error=default_format_error,
            encode=partial(json_encode, pretty=pretty)
        )

        return Response(
            result,
            status=status_code,
            content_type='application/json'
        )

    except HttpQueryError as e:
        return Response(
            json_encode.encode({
                'errors': [default_format_error(e)]
            }),
            status=e.status_code,
            headers=e.headers,
            content_type='application/json'
        )


@app.route('/auth/', methods=['POST'])
def auth():
    login = request.json.get('login', None)
    password = request.json.get('password', None)

    if login is None:
        raise AuthError()

    if password is None:
        raise AuthError()

    db = getClient().planning
    token = resolve(db, login, password)

    return jsonify({'token': token})


@app.errorhandler(AuthError)
def handle_invalid_usage(error):
    response = jsonify({'errors': [{'message': str(error)}]})
    response.status_code = 400
    return response

@app.errorhandler(AuthorisationError)
def handle_token_error(error):
    response = jsonify(error.toDict())
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
    app.run()
