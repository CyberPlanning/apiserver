from flask import Flask, jsonify, current_app, request, render_template, Response, json
from graphql_server import (HttpQueryError, default_format_error,
                            encode_execution_results, json_encode,
                            load_json_body, run_http_query)
from functools import wraps, partial

from .crossdomain import crossdomain
from .authorization import AuthorizationError, requestHandler
from .users import AuthError, resolve, generate_token
from .mongo import getClient
from .schema import schema


app = Flask(__name__)
app.config.from_envvar('CYBERPLANNING_SETTINGS')


@app.route('/graphql/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@crossdomain(origin='*', methods=['GET', 'POST'], headers=["Content-Type", "Authorization"])
def graphql():
    request_method = request.method.lower()
    if request_method == 'get':
        return render_template(
            'graphiql.html',
            graphiql_version="0.11.11",
            graphiql_html_title="Cyber GraphiQL",
        )
    
    # token = requestHandler(request)
    token = {'permission': ['view:*']}

    data = load_json_body(request.data.decode())

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

@app.route('/token/', methods=['POST'])
def token():
    token = requestHandler(request)
    perms = token.get('permission', None)
    if perms is None:
        raise AuthorizationError("No permissions")

    if "user:*" not in perms:
        raise AuthorizationError("Not enough permissions")

    login = request.json.get('login', None)
    duration = request.json.get('duration', None)

    if login is None:
        raise AuthError()
    if duration is None:
        raise AuthError()
    if type(duration) is not int:
        raise AuthError()

    token = generate_token(login, duration)
    return jsonify({'token': token})


@app.errorhandler(HttpQueryError)
def handle_graphql_error(error):
    response = jsonify({'errors': [default_format_error(error)]})
    response.status_code = error.status_code
    response.headers = error.headers
    return response

@app.errorhandler(AuthError)
def handle_auth_error(error):
    response = jsonify({'errors': [{'message': str(error)}]})
    response.status_code = 401
    return response

@app.errorhandler(AuthorizationError)
def handle_token_error(error):
    response = jsonify(error.toDict())
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
    app.run()
