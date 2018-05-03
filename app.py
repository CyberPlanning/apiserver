from flask import Flask, jsonify, current_app, abort
from flask_graphql import GraphQLView
from functools import wraps

from crossdomain import crossdomain

from schema import schema
from schema_v2 import schema as schema_v2

from authorisation import AuthorisationError
from users import AuthError


app = Flask(__name__)
app.config.from_envvar('CYBERPLANNING_SETTINGS')


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


class PlanningGraphQlViewV2(GraphQLView):
    decorators = [
        crossdomain(origin='*', methods=['GET', 'POST'])
    ]

    schema = schema_v2
    graphiql = True  # for having the GraphiQL interface

    @staticmethod
    def format_error(error):
        if hasattr(error, 'original_error') and error.original_error:
            original = error.original_error
            print("\033[33mError\033[0m %s: %s" %
                  (original.__class__.__name__, str(original)))

            formatted = {"message": str(original)}
            if isinstance(original, AuthorisationError):
                formatted['code'] = original.status_code
            if isinstance(original, AuthError):
                formatted['code'] = 403
            return formatted

        return GraphQLView.format_error(error)

    def get_context(self, request):
        return {
            'request': request,
        }


app.add_url_rule(
    '/graphql/v2/',
    view_func=PlanningGraphQlViewV2.as_view('graphqlv2')
)

if __name__ == '__main__':
    app.run()
