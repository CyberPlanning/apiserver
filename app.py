from flask import Flask
from flask_graphql import GraphQLView

from crossdomain import crossdomain
from schema import schema


app = Flask(__name__)


decoratedView = crossdomain(origin='*', headers=['content-type'])(GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True,  # for having the GraphiQL interface
))

app.add_url_rule(
    '/graphql/',
    view_func=decoratedView
)

@app.route('/')
@crossdomain(origin='*')
def index():
    return "Salut"


if __name__ == '__main__':
    app.run()
