
from flask import Flask
from flask_restful import Resource, Api, reqparse
from player import Player
from db import MockStationDB as StationDB
from discovery import ServicePublisher

appl = Flask(__name__)
api = Api(appl)

db = StationDB('stations.db')


class SearchAPI(Resource):

    def __init__(self):

        self.parser = reqparse.RequestParser()
        self.parser.add_argument('term', type=str, required=False)


    def post(self):       

        args = self.parser.parse_args()
        print('got search term %r' % args['term'])

        return db.search(args['term'] if 'term' in args else None)


class PlayerAPI(Resource):

    def __init__(self):

        self.parser = reqparse.RequestParser()
        self.parser.add_argument('state', type=str)


    def get(self):
        
        return { 'level': _player.volume, 'state':  _player.playstate, 'uri': _player.uri, 'duration': _player.duration }


    def post(self):

        args = self.parser.parse_args()
        state = args['state']

        print('received state %s' % state)
        if state == 'play':
            _player.resume()

        elif state == 'stop':
            _player.stop()

        else:
            print('received invalid state %s' % state)
            return '', 400


class VolumeAPI(Resource):    

    def __init__(self):

        self.parser = reqparse.RequestParser()
        self.parser.add_argument('level', type=float)

    def get(self):
        return {'level': _player.volume }
    
    def post(self):        

        args = self.parser.parse_args()
        _player.volume = args['level']

        return ''


class UriAPI(Resource):

     def __init__(self):

        self.parser = reqparse.RequestParser()
        self.parser.add_argument('stream', type=str)

     def get(self):
        return { 'uri': _player.uri, 'duration': _player.duration }

     def put(self):

        args = self.parser.parse_args()
        
        ''' todo should accept uri or stream id from database '''
        _player.play(args['stream'])
        return { 'uri': _player.uri, 'duration': _player.duration }, 201


'''
    API endpoints
'''
api.add_resource(SearchAPI, '/search', endpoint='search')
api.add_resource(PlayerAPI, '/player', endpoint='player')
api.add_resource(VolumeAPI, '/player/volume', endpoint='volume')
api.add_resource(UriAPI,    '/player/uri', endpoint='uri')

if __name__ == '__main__':

    with Player() as _player, ServicePublisher('pauls radio') as sp:

        # without `use_reloader=False` it initialises twice in debug mode :z
        appl.run(host='0.0.0.0', use_reloader=False)
