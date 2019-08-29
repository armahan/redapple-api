from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_claims
from models.eduModel import UserModel

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('user_id',
                    type=int,
                    required=False,
                    help="This field must be integer."
                    )
_user_parser.add_argument('user_name',
                    type=str,
                    required=True,
                    help="This field cannot be blank."
                    )
_user_parser.add_argument('email',
                    type=str,
                    required=True,
                    help="This field cannot be blank."
                    )
_user_parser.add_argument('password',
                    type=str,
                    required=True,
                    help="This field cannot be blank."
                    )
_user_parser.add_argument('auth_level',
                    type=int,
                    required=False,
                    help="This field must be integer."
                    )


class UserRegister(Resource):

    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_email(data['email']):
            return {"message": "A user with that email already exits."}, 400

        user = UserModel(data['user_name'], data['email'],
                         data['password'], data['auth_level'])
        user.save_to_db()

        return {"message": "Student created successfully."}, 201


class UserList(Resource):

    def get(self):
        return {'Users': list(map(lambda x: x.json(), UserModel.query.all()))}, 200


class User(Resource):

    def get(self, id):
        user = UserModel.find_by_id(id)
        if user:
            return user.json()
        return {'message': 'User not found'}, 404
    @jwt_required
    def put(self, id):
        data = _user_parser.parse_args()
        user = UserModel.find_by_id(id)
        if user:
            user.username = data['user_name']
            user.email = data['email']
            user.password = data['password']
            user.auth_level = data['auth_level']
        else:
            user = UserModel(id, **data)

        user.save_to_db()
        return user.json()

    @jwt_required
    def delete(self, id):
        claims = get_jwt_claims()
        if claims['role'] != 'admin':
            return {'message': 'You dont have authority to delete.'}, 401
        users = UserModel.find_by_id(id)
        if users:
            users.delete_from_db()
            return {'message': 'User deleted.'}
        return {'message': 'User not found.'}, 404

class UserLogin(Resource):

    @classmethod
    def post(cls):
        login_parser = reqparse.RequestParser()
        login_parser.add_argument('email',
                    type=str,
                    required=True,
                    help="This field cannot be blank."
                    )
        login_parser.add_argument('password',
                    type=str,
                    required=True,
                    help="This field cannot be blank."
                    )
        data = login_parser.parse_args()

        user= UserModel.find_by_email(data['email'])
        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.json(),
            fresh=True)
            refresh_token = create_refresh_token(user.json())
            return {
                'user_id': user.id,
                'user_name': user.username,
                'auth_level': user.auth_level,
                'access_token' : access_token,
                'refresh_token' : refresh_token
            }, 200
        return {'message': 'Invalid credentials'}, 401
