from database import db

tags = db.Table('tags',
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True),
    db.Column('content_id', db.Integer, db.ForeignKey('contents.id'), primary_key=True)
)

test_in_question = db.Table('testinquestions',
    db.Column('test_id', db.Integer, db.ForeignKey('tests.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id'), primary_key=True)
)

content_owners = db.Table('contentowners',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('content_id', db.Integer, db.ForeignKey('contents.id'), primary_key=True)
)

level_owners = db.Table('levelowners',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('level_id', db.Integer, db.ForeignKey('levels.id'), primary_key=True)
)

game_owners = db.Table('gameowners',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'), primary_key=True)
)

test_owners = db.Table('testowners',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('test_id', db.Integer, db.ForeignKey('tests.id'), primary_key=True)
)

question_owners = db.Table('questionowners',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id'), primary_key=True)
)

subscribes = db.Table('subscribes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'), primary_key=True)
)

class ContentInLevelModel(db.Model):
    __tablename__ = 'coninlevels'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('contents.id'), primary_key=True)
    weight = db.Column(db.Integer)

    content = db.relationship('ContentModel', backref=db.backref("coninlevels", cascade="all, delete-orphan"))
    level = db.relationship('LevelModel', backref=db.backref("coninlevels", cascade="all, delete-orphan"))

    def __init__(self, level=None, content=None, weight=None):
        self.level = level
        self.content = content
        self.weight = weight

    def json(self):
        return {'level_id': self.level_id, 'content_id': self.content_id, 'weight': self.weight}

    @classmethod
    def find_by_level_id(cls, _id):
        return cls.query.filter_by(level_id=_id).all()

    @classmethod
    def find_by_level_id_first(cls, _id):
        return cls.query.filter_by(level_id=_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class TestInLevelModel(db.Model):
    __tablename__ = 'testinlevels'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), primary_key=True)
    weight = db.Column(db.Integer)

    test = db.relationship('TestModel',  backref=db.backref("testinlevels", cascade="all, delete-orphan"))
    level = db.relationship('LevelModel', backref=db.backref("testinlevels", cascade="all, delete-orphan"))

    def json(self):
        return {'level_id': self.level_id, 'test_id': self.test_id, 'weight': self.weight}
    
    def __init__(self, level=None, test=None, weight=None):
        self.level = level
        self.test = test
        self.weight = weight

    @classmethod
    def find_by_level_id(cls, _id):
        return cls.query.filter_by(level_id=_id).all()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class LevelInGameModel(db.Model):
    __tablename__ = 'levelingames'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), primary_key=True)
    weight = db.Column(db.Integer)

    game = db.relationship('GameModel', backref=db.backref("levelingames", cascade="all, delete-orphan"))
    level = db.relationship('LevelModel', backref=db.backref("levelingames", cascade="all, delete-orphan"))

    def __init__(self, game=None, level=None, weight=None):
        self.game = game
        self.level = level
        self.weight = weight

    def json(self):
        return {'level_id': self.level_id, 'weight': self.weight}

    @classmethod
    def find_by_game_id(cls, _id):
        return cls.query.filter_by(game_id=_id).all()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    auth_level = db.Column(db.Integer, nullable=True)
    
    games = db.relationship('GameModel', secondary=game_owners, backref='game_owners')
    questions = db.relationship('QuestionModel', secondary=question_owners, backref='question_owners')
    class_name = db.relationship('ClassNameModel', lazy='dynamic')
    student_class = db.relationship('StudentClassModel', lazy='dynamic')
    student_level = db.relationship('StudentLevelModel', lazy='dynamic')



    def __init__(self, username, email, password, authlevel):
        self.username = username
        self.email = email
        self.password = password
        self.auth_level = authlevel
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def json(self):
        return {'user_id': self.id, 'user_name': self.username, 'email': self.email, 'auth_level': self.auth_level}

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_name(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class ClassNameModel(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)

    teacher = db.relationship('UserModel')
    student_class = db.relationship('StudentClassModel', lazy='dynamic')

    def __init__(self, teacher_id, name):
        self.teacher_id = teacher_id
        self.name = name

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def json(self):
        return {'class_id': self.id,'teacher_id': self.teacher_id, 'class_name': self.name}

    def json_name(self):
        return {'name': self.name}

    @classmethod
    def find_by_teacher_id(cls, teacher_id):
        return cls.query.filter_by(teacher_id=teacher_id).all()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()


class StudentClassModel(db.Model):
    __tablename__ = 'studentclasses'

    id = db.Column(db.Integer, primary_key=True)
    class_name_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    class_name = db.relationship('ClassNameModel')
    user = db.relationship('UserModel')

    def __init__(self, class_name_id, student_id):
        self.class_name_id = class_name_id
        self.student_id = student_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def json(self):
        return {'class_name_id': self.class_name_id, 'student_id': self.student_id}

    @classmethod
    def find_by_classname_id(cls, class_name_id):
        return cls.query.filter_by(class_name_id=class_name_id).all()

    @classmethod
    def find_by_student_id(cls, student_id):
        return cls.query.filter_by(student_id=student_id).all()

class StudentLevelModel(db.Model):
    __tablename__ = 'studentlevels'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'))
    is_done = db.Column(db.Boolean)

    user = db.relationship('UserModel')
    level = db.relationship('LevelModel')

    def __init__(self, student_id, level_id, is_done):
        self.student_id = student_id
        self.level_id = level_id
        self.is_done = is_done

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def json(self):
        return {'student_id': self.student_id, 'level_id': self.level_id, 'is_done': self.is_done}

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_student_id(cls, student_id):
        return cls.query.filter_by(student_id=student_id).first()

    @classmethod
    def find_by_student_id_all(cls, student_id):
        return cls.query.filter_by(student_id=student_id).all()

    @classmethod
    def find_by_level_id(cls, level_id):
        return cls.query.filter_by(level_id=level_id).all()


class LevelModel(db.Model):
    __tablename__ = 'levels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80))

    owner = db.relationship('UserModel', secondary=level_owners, backref='level_owners')
    student_level = db.relationship('StudentLevelModel', lazy='dynamic')
    contents = db.relationship('ContentModel', secondary="coninlevels", viewonly=True)
    tests = db.relationship('TestModel', secondary="testinlevels", viewonly=True)
    #games = levels = db.relationship('GameModel', secondary="levelingames", viewonly=True)

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.contents = []
        self.tests = []

    def rollback_db(self):
        db.session.rollback()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {'level_id': self.id, 'level_name': self.name, 'level_description': self.description}
    
    def add_contents(self, content, weight):
        self.coninlevels.append(ContentInLevelModel(level=self, content=content, weight=weight))
    
    def add_tests(self, test, weight):
        self.testinlevels.append(TestInLevelModel(level=self, test=test, weight=weight))
    
    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()


class GameModel(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80))

    owner = db.relationship('UserModel', secondary=game_owners, backref='game_owners')
    subscribe = db.relationship('UserModel', secondary=subscribes, backref='subscribe')
    levels = db.relationship('LevelModel', secondary="levelingames", viewonly=True)

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.levels = []

    def json(self):
        return {'game_id': self.id, 'game_name': self.name, 'game_description': self.description}

    def rollback_db(self):
        db.session.rollback()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def add_levels(self, level, weight):
        self.levelingames.append(LevelInGameModel(game=self, level=level, weight=weight))

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class TestModel(db.Model):
    __tablename__ = 'tests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    owner = db.relationship('UserModel', secondary=test_owners, backref='test_owners')
    question = db.relationship('QuestionModel', secondary=test_in_question, backref='questions')
    levels = db.relationship('LevelModel', secondary="testinlevels", viewonly=True)

    def __init__(self, name):
        self.name = name
        self.question = []

    def json(self):
        return {'test_id': self.id, 'test_name': self.name}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class QuestionModel(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    code = db.Column(db.String(80))
    question = db.Column(db.Text)

    owner = db.relationship('UserModel', secondary=question_owners, backref='question_owners')
    subject = db.relationship('SubjectModel')
    options = db.relationship('OptionModel', backref='question')

    def __init__(self, code, question, subject_id=None):
        self.code = code
        self.question = question
        self.subject_id = subject_id
        self.options = []

    def json(self):
        return {'question_id': self.id, 'code': self.code, 'question': self.question, 'subject_id': self.subject_id}
    
    def add_options(self, answer, is_true):
        self.options.append(OptionModel(question=self, answer=answer, is_true=is_true))

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_code(cls, code):
        return cls.query.filter_by(code=code).first()

    @classmethod
    def find_by_subject_id(cls, subject_id):
        return cls.query.filter_by(subject_id=subject_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class OptionModel(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    answer = db.Column(db.Text)
    is_answer = db.Column(db.Boolean)

    def json(self):
        return {'answer': self.answer, 'is_true': self.is_answer}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_question_id(cls, question_id):
        return cls.query.filter_by(question_id=question_id).all()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()


class SubjectModel(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    name = db.Column(db.String(80), nullable=False)

    content = db.relationship('ContentModel', secondary=tags, backref='tag_content')
    parent = db.relationship('SubjectModel', remote_side=id, backref='parent_subject')

    def __init__(self, name=None, parent_id=None, _id=None):
        self.name = name
        self.parent_id = parent_id
        self.id = _id


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def json(self):
        return {"subject_id": self.id, "parent_id": self.parent_id, "subject_name": self.name}

    @classmethod
    def find_by_subject_id(cls, subject_id):
        return cls.query.filter_by(id=subject_id).first()

    @classmethod
    def find_by_child_id(cls, subject_id):
        return cls.query.filter_by(parent_id=subject_id).first()
    @classmethod
    def find_by_subject_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class ContentModel(db.Model):
    __tablename__ = 'contents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    text = db.Column(db.Text)

    owner = db.relationship('UserModel', secondary=content_owners, backref='content_owners')
    subject = db.relationship('SubjectModel', secondary=tags, backref='tag_subject')
    levels = db.relationship('LevelModel', secondary="coninlevels", viewonly=True)

    def __init__(self, name, text, _id=None):
        self.name = name
        self.text = text
        self.id = _id
        self.levels = []

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {'content_id': self.id, 'content_name': self.name, 'content': self.text}

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()
