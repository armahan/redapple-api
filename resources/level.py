from flask_restful import Resource
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity
from models.eduModel import LevelModel, GameModel, TestModel, ContentModel, ContentInLevelModel, TestInLevelModel, \
    LevelInGameModel, UserModel


class LevelCreate(Resource):
    @jwt_required
    def post(self):
        claims = get_jwt_claims()
        req_data = request.get_json()
        name = req_data.get('level_name')
        contents = req_data.get('contents')
        description = req_data.get('level_description')
        user = UserModel.find_by_id(claims['user_id'])
        if LevelModel.find_by_name(name):
            return {"message": " Level already exits."}, 400
        level = LevelModel(name, description)
        if contents:
            for cont in contents:
                con_id = 0
                con_weg = 0
                te_id = 0
                te_weg = 0
                if 'content_id' in cont:
                    con_id = cont['content_id']
                    con_weg = cont['weight']
                    #return{'cont': cont['content_id'], 'weg': cont['weight']}      
                    cont = ContentModel.find_by_id(con_id)
                    level.add_contents(cont, con_weg)
                elif 'test_id' in cont:
                    te_id = cont['test_id']
                    te_weg = cont['weight']
                    test = TestModel.find_by_id(te_id)
                    level.add_tests(test, te_weg)
        level.owner.append(user)
        level.save_to_db()
        #return{'error':'There is an error!!!'}, 500
        return {"level_id": level.id}, 201


class LevelList(Resource):
    @jwt_required
    def get(self):
        return {'Levels': list(map(lambda x: x.json(), LevelModel.query.all()))}

class Level(Resource):
    @jwt_required
    def get(self, id):
        level = LevelModel.find_by_id(id)
        if level:
            contents = list(map(lambda x: x.json(), level.contents))
            tests = list(map(lambda x: x.json(), level.tests))
            test_weights = TestInLevelModel.find_by_level_id(level.id)
            content_weights = ContentInLevelModel.find_by_level_id(level.id)
            content_weight = list(map(lambda x: x.json(), content_weights))
            test_weight = list(map(lambda x: x.json(), test_weights))

            combine = []
            for content in contents:
                for c_weight in content_weight:
                    if content['content_id'] == c_weight['content_id']:
                        content.update(c_weight)
                        combine.append(content)
            for test in tests:
                for t_weight in test_weight:
                    if test['test_id'] == t_weight['test_id']:
                        test.update(t_weight)
                        combine.append(test)
            #combine = sorted(combine, key=lambda x: x['weight'])
            return {'level_name': level.name, 'level_description': level.description, 'contents': combine}, 200
        return {'message': 'There is not such a level.'}, 404

    @jwt_required
    def put(self, id):
        req_data = request.get_json()
        level = LevelModel.find_by_id(id)
        contents = req_data.get('contents')
        if level:
            level.name = req_data.get('level_name')
            level.description = req_data.get('level_description')
            delete_test = TestInLevelModel.find_by_level_id(level.id)
            delete_content = ContentInLevelModel.find_by_level_id(level.id)
            for delete in delete_content:
                delete.delete_from_db()
            for delete in delete_test:
                delete.delete_from_db()
            for cont in contents:
                con_id = 0
                con_weg = 0
                te_id = 0
                te_weg = 0
                if 'content_id' in cont:
                    con_id = cont['content_id']
                    con_weg = cont['weight']
                    #return{'cont': cont['content_id'], 'weg': cont['weight']}      
                    cont = ContentModel.find_by_id(con_id)
                    level.add_contents(cont, con_weg)
                elif 'test_id' in cont:
                    te_id = cont['test_id']
                    te_weg = cont['weight']
                    #return{'cont': cont['test_id'], 'weg': cont['weight']} 
                    test = TestModel.find_by_id(te_id)
                    level.add_tests(test, te_weg)
            level.save_to_db()
            return {'level_name': level.name}, 200
        return {'message': 'There is not such a level.'}, 404
    @jwt_required
    def delete(self, id):
        level = LevelModel.find_by_id(id)
        if level:
            level.delete_from_db()
            return {'message': 'level deleted.'}, 200
        return {'message': 'There is not such a level.'}, 404

class ContentByLevel(Resource):
    @jwt_required
    def get(self, _id):
        levels = LevelModel.find_by_id(_id)
        if levels:
            combine = list(map(lambda x: x.json(), levels.contents)) + list(map(lambda x: x.json(), levels.tests))
            return{'contents': combine }, 200
        return {'message': 'Level not found.'}, 404

class GameCreate(Resource):
    @jwt_required
    def post(self):
        claims = get_jwt_claims()
        data = request.get_json()
        name = data.get('game_name')
        description = data.get('game_description')
        levels = data.get('levels')
        user = UserModel.find_by_id(claims['user_id'])
        if GameModel.find_by_name(name):
            return {"message": " Game already exits."}, 400
        game = GameModel(name, description)
        if levels:
            for level in levels:
                l_id = 0
                l_weg = 0
                if 'level_id' in level:
                    l_id = level['level_id']
                    l_weg = level['weight']
                    #return{'level': l_id, 'weg': l_weg}, 200
                    find_level = LevelModel.find_by_id(l_id)
                    game.add_levels(find_level, l_weg)
        game.owner.append(user)
        game.save_to_db()
        return {"message": "Game created successfully.", 'game_id': game.id, 'game_name': game.name}, 201


class GameList(Resource):

    def get(self):
        return {'games': list(map(lambda x: x.json(), GameModel.query.all()))}



class Game(Resource):
    @jwt_required
    def get(self, id):
        game = GameModel.find_by_id(id)
        if game:
            game_weight = LevelInGameModel.find_by_game_id(id)
            levels = list(map(lambda x: x.json(), game.levels))
            weights =  list(map(lambda x: x.json(), game_weight))
            combine = []
            for level in levels:
                for weight in weights:
                    if level['level_id'] == weight['level_id']:
                        level.update(weight)
                        combine.append(level)
            return {'game_name': game.name, 'levels': combine}, 200
        return {'message': 'There is not such a game.'}, 404
    @jwt_required
    def put(self, id):
        data = request.get_json()
        game = GameModel.find_by_id(id)    
        if game:
            level_del = LevelInGameModel.find_by_game_id(game.id)
            for delete in level_del:
                delete.delete_from_db()
            game.name = data.get('game_name')
            game.description = data.get('game_description')
            game.is_published = data.get('game_published')
            if data.get('levels'):
                levels = data.get('levels')
                for level in levels:
                    l_id = 0
                    l_weg = 0
                    if 'level_id' in level:
                        l_id = level['level_id']
                        l_weg = level['weight']
                        #return{'level': l_id, 'weg': l_weg}, 200
                        find_level = LevelModel.find_by_id(l_id)
                        game.add_levels(find_level, l_weg)
            game.save_to_db()
            return {'game_name': game.name, 'levels': list(map(lambda x: x.json(), game.levels))}, 200
        return {'message': 'There is not such a game.'}, 404

    @jwt_required
    def delete(self, id):
        game = GameModel.find_by_id(id)
        users = game.query.filter_by(
            id=game.id).first().owner
        if game:
            if users:
                for user in users:
                    rm = UserModel.find_by_id(user.id)
                    game.owner.remove(rm)
                    game.save_to_db()
                game.delete_from_db()
                return {'message': game.name+ ' is deleted.'}, 200
        return {'message': 'There is not such a game.'}


class GameLevels(Resource):
    @jwt_required
    def get(self, id):
        game = GameModel.find_by_id(id)
        if game:
            level_body = []
            for levels in game.levels:
                app = {}
                level = LevelModel.find_by_id(levels.level_id)
                app['level'] = level.name
                app['weight'] = levels.weight
                level_body.append(app)
            level_body = sorted(level_body, key=lambda x: x['weight'])
            return {'game_name': game.name, 'levels': level_body}
        return {'message': 'There is not such a game.'}

class GameSubscribe(Resource):
    @jwt_required
    def post(self):
        claims = get_jwt_claims()
        req_data = request.get_json()
        get_user = UserModel.find_by_id(claims['user_id'])
        get_game = GameModel.find_by_id(req_data.get('game_id'))
        if get_user and get_game:
            get_game.subscribe.append(get_user)
            get_game.save_to_db()
            return {'message': 'Subscribed to ' + get_game.name}
        return {'message': 'Game or User not found.'}

class GetSubscribedGames(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        user = UserModel.find_by_id(claims['user_id'])
        if user:
            return {'games': list(map(lambda x: x.json(), user.query.filter_by(id=user.id).first().subscribe))}, 200
        return {'message': 'User not found.'}, 404

class GamesByUser(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        user = UserModel.find_by_id(claims['user_id'])
        if user:
            return{
                'games': list(map(lambda x: x.json(), user.query.filter_by(id=user.id).first().games))}, 200
        return {'message': 'User not found.'}, 404