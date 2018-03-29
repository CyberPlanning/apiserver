from flask import Flask, jsonify, current_app
from flask_graphql import GraphQLView
from functools import wraps

from crossdomain import crossdomain
from schema import schema

from jwtHandler import JWTError, requestHandler

app = Flask(__name__)

app.debug = True
app.config['JWT_SECRET_KEY'] = "Flag{Not_so_n00b}"


class AuthorizationMiddleware(object):
    def resolve(self, next, root, info, **args):
        # print("Middleware", info.operation)
        # raise Exception("Hacked by AuR3voirCTF")
        return next(root, info, **args)


class PlanningGraphQlView(GraphQLView):
    decorators = [
        crossdomain(origin='*', methods=['GET', 'POST'])
    ]

    middleware = [
        # AuthorizationMiddleware()
    ]

    schema = schema
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
    '/graphql/',
    view_func=PlanningGraphQlView.as_view('graphql')
)

if __name__ == '__main__':
    app.run()


