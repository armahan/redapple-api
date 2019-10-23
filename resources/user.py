from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_claims, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt
from models.eduModel import UserModel, RevokedTokenModel

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
                    required=False,
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
    @jwt_required
    def get(self):
        return {'users': list(map(lambda x: x.json(), UserModel.query.all()))}, 200


class User(Resource):
    @jwt_required
    def get(self, id):
        user = UserModel.find_by_id(id)
        if user:
            return user.json()
        return {'message': 'User not found'}, 404
    @jwt_required
    def put(self, id):
        claims = get_jwt_claims()
        data = _user_parser.parse_args()
        user = UserModel.find_by_id(id)
        if user or claims['role'] == 'admin':
            user.username = data['user_name']
            user.email = data['email']
            user.auth_level = data['auth_level']
            if data['password']:
                user.password = data['password']
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
                'access_token' : access_token,
                'refresh_token' : refresh_token
            }, 200
        return {'message': 'Invalid credentials'}, 401

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}, 200

class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500