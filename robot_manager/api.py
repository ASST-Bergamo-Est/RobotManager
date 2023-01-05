import json

from flask import request
from flask_restful import Api, Resource
from . import __version__
from robot_manager import robot_manager

class RobotManagerApi(Api):
    def __init__(self, *args, **kwargs):
        super(RobotManagerApi, self).__init__(*args, **kwargs)
        self.add_resource(Helloworld, '/')
        self.add_resource(Version, '/version')
        self.add_resource(CheckAction, '/action/check/<string:action_id>')
        self.add_resource(RequestAction, '/action/<string:action>/<string:machine>/<string:position>/<string:plate_name>')


class Helloworld(Resource):
    def get(self):
        return {'hello': 'world'}


class Version(Resource):
    def get(self):
        return {
            'name': 'RobotManager server',
            'version': '{}'.format(__version__)
        }


class CheckAction(Resource):
    def get(self, action_id):
        return {'state': 'not impmlemented'}


class RequestAction(Resource):
    def post(self, action, machine, position, plate_name):
        try:
            print("Received options: {}".format(request.get_json()))
        except TypeError as e:
            print("Got error: {}".format(e))
        return {'action_id': 'fake-id'}