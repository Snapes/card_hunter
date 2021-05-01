from flask import Flask
from flask_restful import Resource, Api, reqparse
from CardSearcher import CardSearcher

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('card', type=str, help='card name to search')
        args = parser.parse_args()
        card_searcher = CardSearcher()
        return card_searcher.search_card(args['card'])

    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)

