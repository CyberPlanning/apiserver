from flask import Flask, jsonify, current_app
from flask_graphql import GraphQLView
from functools import wraps

from crossdomain import crossdomain
from schema import schema

from jwtHandler import JWTError, requestHandler

app = Flask(__name__)

app.debug = True
app.config['JWT_SECRET_KEY'] = "Flag{Not_so_n00b}"


class PlanningGraphQlView(GraphQLView):
    decorators = [
        crossdomain(origin='*', methods=['GET', 'POST'])
    ]

    schema = schema
    graphiql = True  # for having the GraphiQL interface

    def get_context(self, request):
        return {
            'request': request,
        }

app.add_url_rule(
    '/graphql/',
    view_func=PlanningGraphQlView.as_view('graphql')
)

@app.errorhandler(JWTError)
def authError(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
    app.run()


