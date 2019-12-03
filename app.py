from flask import Flask, request, Blueprint
from flask_restful import Api
from flask_jwt_extended import JWTManager, get_jwt_identity
from datetime import timedelta

from database import db
from resources.user import User, UserRegister, UserList, UserLogin, TokenRefresh, UserLogoutAccess, UserLogoutRefresh
from resources.classname import ClassNameRegister, ClassNameList, ClassListByTeacher
from resources.studentclass import StudentClassRegister, StudentInClass
from resources.level import LevelCreate, GameCreate, LevelList, GameList, Level, Game, GameLevels, ContentByLevel, GameSubscribe, GamesByUser, GetSubscribedGames
from resources.studentlevel import StudentLevel, StudentLevelList, StudentLevelUpdate
from resources.subject import SubjectRegister, Subject, SubjectList
from resources.content import ContentPost, ContentList, Content, ContentBySubject, ContentsByUser
from resources.exam import QuestionPost, Question, Questions, QuestionByUser, TestPost, Test, Tests, TestsByUser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:q1w2e3@127.0.0.1:3306/course-turkish'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'SHrjb66PHh5XrBaM'
api = Api(app)
api.prefix = '/api/v0.1'


@app.before_first_request
def create_tables():
    db.create_all()
jwt = JWTManager(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity['auth_level'] == 1:
        return {'role': 'admin', 'user_id': identity['user_id']}
    elif identity['auth_level'] == 2:
        return {'role': 'teacher', 'user_id': identity['user_id']}
    return {'role': 'student', 'user_id': identity['user_id']}

api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')

api.add_resource(UserLogoutAccess, '/logout/access')
api.add_resource(UserLogoutRefresh, '/logout/refresh')

api.add_resource(User, '/user/<int:id>')
api.add_resource(UserRegister, '/user/register')
api.add_resource(UserList, '/users')

api.add_resource(GameSubscribe, '/subscribe')
api.add_resource(GetSubscribedGames, '/subscribe/user')

api.add_resource(ClassNameRegister, '/class/register')
api.add_resource(ClassNameList, '/classes')
api.add_resource(ClassListByTeacher, '/class/teacher/<int:teacher_id>')

api.add_resource(StudentClassRegister, '/class/student/register')
api.add_resource(StudentInClass, '/class/student/<int:student_id>')

api.add_resource(LevelCreate, '/level/create')
api.add_resource(LevelList, '/levels')
api.add_resource(Level, '/level/<int:id>')
api.add_resource(ContentByLevel, '/contentbylevel/<int:_id>')

api.add_resource(GameCreate, '/game/create')
api.add_resource(GameList, '/games')
api.add_resource(Game, '/game/<int:id>')
api.add_resource(GameLevels, '/game/<int:id>/levels')

api.add_resource(GamesByUser, '/games/user')

api.add_resource(StudentLevel, '/level/student')
api.add_resource(StudentLevelUpdate, '/level/<int:student_id>/<int:level_id>')
api.add_resource(StudentLevelList, '/level/student/<int:student_id>')

api.add_resource(SubjectList, '/subjects')
api.add_resource(SubjectRegister, '/subject/register')
api.add_resource(Subject, '/subject/<int:id>')

api.add_resource(ContentPost, '/content/create')
api.add_resource(ContentList, '/contents')
api.add_resource(Content, '/content/<int:id>')
api.add_resource(ContentBySubject, '/contentbysubject/<int:id>')

api.add_resource(ContentsByUser, '/contents/user')

api.add_resource(QuestionPost, '/question/create')
api.add_resource(Questions, '/questions')
api.add_resource(Question, '/question/<int:id>')
api.add_resource(QuestionByUser, '/questions/user')

api.add_resource(TestPost, '/test/create')
api.add_resource(Test, '/test/<int:id>')
api.add_resource(Tests, '/tests')

api.add_resource(TestsByUser, '/tests/user')

if __name__ == '__main__':
    from database import db
    db.init_app(app)
    app.run(port=5000, debug=True)
