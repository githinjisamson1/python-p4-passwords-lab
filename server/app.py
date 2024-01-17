#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User


class Index(Resource):
    def get(self):
        return "Authentication System"


class ClearSession(Resource):

    def delete(self):

        session['page_views'] = None
        session['user_id'] = None

        return {}, 204


class Signup(Resource):

    def post(self):
        json = request.get_json()
        user = User(
            username=json['username'],
            password_hash=json['password']
        )
        db.session.add(user)
        db.session.commit()

        # set session
        session["user_id"] = user.id
        return user.to_dict(), 201


# !default check_session => upon refresh
class CheckSession(Resource):
    def get(self):
        # session is not empty
        user = session.get("user_id")

        if not user:
            return {}, 204

        else:
            user = User.query.filter_by(id=session.get("user_id")).first()
            return user.to_dict(), 200


# !default login
class Login(Resource):
    def post(self):
        # user credentials
        data = request.get_json()

        # check in db
        user = User.query.filter_by(username=data.get("username")).first()

        # not found => unauthorized
        if not user:
            return {}, 401

        else:
            password = data.get("password")
            # check if passwords match
            if user.authenticate(password):
                # set session
                session["user_id"] = user.id
                return user.to_dict(), 200


# !default logout
class Logout(Resource):
    def delete(self):
        # destroy session
        session["user_id"] = None

        # no content
        return {}, 204


api.add_resource(Index, "/")
api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Logout, '/logout', endpoint='logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
