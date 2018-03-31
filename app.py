from flask import Flask, jsonify, current_app
from flask_graphql import GraphQLView
from functools import wraps

from crossdomain import crossdomain

from schema import schema
from schema_v2 import schema as schema_v2


app = Flask(__name__)
app.config.from_envvar('CYBERPLANNING_SETTINGS')


class AuthorizationMiddleware(object):
    def resolve(self, next, root, info, **args):
        # print("Middleware", info.operation)
        # raise Exception("Hacked by AuR3voirCTF")
        return next(root, info, **args)


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

    middleware = [
        # AuthorizationMiddleware()
    ]

    schema = schema_v2
    graphiql = True  # for having the GraphiQL interface

    def get_context(self, request):
        return {
            'request': request,
        }

    # def dispatch_request(self):
    #     ret = super().dispatch_request()
    #     print(ret.data, dir(ret))
    #     return ret

app.add_url_rule(
    '/graphql/v2/',
    view_func=PlanningGraphQlViewV2.as_view('graphqlv2')
)

if __name__ == '__main__':
    app.run()


