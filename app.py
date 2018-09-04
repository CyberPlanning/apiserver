from flask import Flask, jsonify, current_app, abort, request, render_template
from flask_graphql import GraphQLView
from functools import wraps

from crossdomain import crossdomain

from schema import schema

from authorisation import AuthorisationError, requestHandler
from users import AuthError, resolve
from mongo import getClient


app = Flask(__name__)
app.config.from_envvar('CYBERPLANNING_SETTINGS')


class PlanningGraphQlView(GraphQLView):
    decorators = [
        crossdomain(origin='*', methods=['GET', 'POST'])
    ]

    schema = schema
    graphiql = True  # for having the GraphiQL interface
    graphiql_version = '0.11.11'
    graphiql_html_title = 'Cyberplanning API'

    def get_context(self):
        # Check JWT token
        token = requestHandler(request)
        app.logger.info('Token %s' % token)

        return {
            'token': token
        }

    def render_graphiql(self, params, result):
        return render_template(
            'graphiql.html',
            params=params,
            result=result,
            graphiql_version=self.graphiql_version,
            graphiql_html_title=self.graphiql_html_title,
        )


app.add_url_rule(
    '/graphql/',
    view_func=PlanningGraphQlView.as_view('graphql')
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
