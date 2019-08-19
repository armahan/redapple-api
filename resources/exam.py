from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_claims
from models.eduModel import QuestionModel, OptionModel, TestModel, UserModel


class QuestionPost(Resource):
    def post(self):
        req_data = request.get_json()
        code = req_data.get('code')
        subject = req_data.get('subject_id')
        question = req_data.get('question')
        answers = req_data.get('options')
        user = UserModel.find_by_id(req_data.get('user_id'))

        if QuestionModel.find_by_code(code):
            return {'message': 'Question is already exists.'}, 400
        question_add = QuestionModel(code, question, subject)
        question_add.owner.append(user)

        for opt in answers:
            answer = ''
            is_true = False
            for add in opt:
                if 'answer' == add:
                    answer = opt[add]
                elif 'is_true' == add:
                    is_true = opt[add]
            save_answer = OptionModel(question = question_add, answer = answer, is_answer = is_true)
            question_add.options.append(save_answer)
            question_add.save_to_db()
            #save_answer.save_to_db()
        return {'message': 'Question is created.'}, 201

class Questions(Resource):
    def get(self):
        return {'Questions': list(map(lambda x: x.json(), QuestionModel.query.all()))}

class Question(Resource):

    def get(self, id):
        question = QuestionModel.find_by_id(id)
        if question:
            return {'question': question.question, 'options': list(map(lambda x: x.json(), question.options))}, 200
        return {'message': 'Question not found.'}, 400

    def put(self, id):
        code = QuestionModel.find_by_id(id)
        req_data = request.get_json()
        subject = req_data.get('subject')
        question = req_data.get('question')
        answers = req_data.get('options')
        if code:
            code.code = req_data.get('code')
            code.subject_id = subject
            code.question = question
            options = OptionModel.find_by_question_id(code.id)
            for option in options:
                option.delete_from_db()
            for opt in answers:
                answer = ''
                is_true = False
                for add in opt:
                    if 'answer' == add:
                        answer = opt[add]
                    elif 'is_true' == add:
                        is_true = opt[add]
                save_answer = OptionModel(question = code, answer = answer, is_answer = is_true)
                code.options.append(save_answer)
            code.save_to_db()
            return {'message': 'Updated'}, 200
        return {'message': 'Question not found.'}, 400

    def delete(self, id):
        code = QuestionModel.find_by_id(id)
        if code:
            answers = OptionModel.find_by_question_id(code.id)
            for answer in answers:
                answer.delete_from_db()
            code.delete_from_db()
            return {'message': 'Question deleted.'}, 200
        return {'message': 'Question not found.'}, 400

class TestPost(Resource):

    def post(self):
        req_data = request.get_json()
        questions = req_data.get('questions')
        test = req_data.get('test_name')
        user = UserModel.find_by_id(req_data.get('user_id'))
        if TestModel.find_by_name(test):
            return {'message': 'Test is already exists.'}, 400
        name = TestModel(test)
        for quest in questions:
            for q in quest:
                question = QuestionModel.find_by_id(quest[q])
                name.question.append(question)
        name.owner.append(user)
        name.save_to_db()
        return {'message': 'Test is created.'}, 201


class Tests(Resource):

    def get(self):
        return {'Questions': list(map(lambda x: x.json(), TestModel.query.all()))}, 200


class Test(Resource):

    def get(self, id):
        test = TestModel.find_by_id(id)
        if test:
            in_questions = []
            for quest in test.question:
                add = {}
                question = QuestionModel.find_by_id(quest.id)
                add['question_id'] = question.id
                add['question'] = question.question
                add['options'] = list(map(lambda x: x.json(), question.options))
                in_questions.append(add)

            return {'test_name': test.name, 'questions': in_questions}, 200
        return {'message': 'Test is not found.'}, 400
    def put(self, id):
        req_data = request.get_json()
        questions = req_data.get('questions')
        test = TestModel.find_by_id(id)
        if test:
            old_questions = test.question
            for quest in old_questions:
                question = QuestionModel.find_by_id(quest.id)
                test.question.remove(question)
                test.save_to_db()
            test.name = req_data.get('name')
            for quest in questions:
                for q in quest:
                    question = QuestionModel.find_by_id(quest[q])
                    test.question.append(question)
                test.save_to_db()
            return {'message': 'Successfully updated.'}, 200
        return {'message': 'Test is not found.'}, 400

    def delete(self, id):
        test = TestModel.find_by_id(id)
        if test:
            test.delete_from_db()
            return {'message': 'Test is deleted.'}, 200
        return {'message': 'Test is not found.'}, 400
