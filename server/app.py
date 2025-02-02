#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
db.init_app(app)
migrate = Migrate(app, db)



api = Api(app)
@app.route('/')
def home():
    return ''


class Campers(Resource):
    def get(self):
        campers = []
        for camper in Camper.query.all():
            camper_json={
                'id': camper.id,
                'name': camper.name,
                'age': camper.age
			}
            campers.append(camper_json)
        return make_response(campers, 200)
    

    def post(self):
        
        try:
            new_camper = Camper(name = request.get_json()['name'], age = request.get_json()['age'])
            db.session.add(new_camper)
            db.session.commit()
            new_camper_json = {
                'id' :  new_camper.id,
                'name' : new_camper.name,
                'age' : new_camper.age
			}
            return make_response(new_camper_json, 201)
        except Exception as e:
            return  make_response({ "errors": [str(e)] }, 400)
            
        
class Campers_by_id(Resource):


    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()        
        if not camper:
            return {"error": "Camper not found"}, 404
        return camper.to_dict(), 200
    

    def patch(self,id):
        camper = Camper.query.filter_by(id=id).first()        
        if not camper:
            return {"error": "Camper not found"}, 404
	    
        try:
            for attr in request.get_json():
                setattr(camper,attr,request.get_json()[attr])
            db.session.add(camper)
            db.session.commit()
            updated_camper = {
            'id' : camper.id,
            'name' : camper.name,
            'age' : camper.age
		      }
            return make_response(updated_camper, 202)
        except Exception as e:
            return make_response({ "errors": ["validation errors"]}, 400)
	



class Activities(Resource):
    def get(self):
        activities = [activity.to_dict() for activity in Activity.query.all() ]
        return make_response(activities, 200)
    
class Activity_by_id(Resource):
    def delete(self,id):
        activity = Activity.query.filter_by(id=id).first()
        
        if not activity:
            return make_response({"error": "Activity not found"}, 404)

        db.session.delete(activity)
        db.session.commit()
        return {},204



class SignupResource(Resource):
    def post(self):
        try:
            new_signup = Signup(camper_id = request.get_json()['camper_id'], 
            activity_id = request.get_json()['activity_id'], time= request.get_json()['time'])
            db.session.add(new_signup)
            db.session.commit()
            return  new_signup.to_dict(), 201
        except :
            return make_response({ 'errors': ["validation errors"]}, 400)



api.add_resource(Campers, '/campers')
api.add_resource(Campers_by_id, '/campers/<int:id>')
api.add_resource(Activities, '/activities')
api.add_resource(Activity_by_id, '/activities/<int:id>' )
api.add_resource(SignupResource, '/signups')
if __name__ == '__main__':
    app.run(port=5555, debug=True)
