from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
# reqparse ensures that we pass the information needed to make a specific request

# creating a Flask app
app = Flask(__name__) 

# wrap our app in an api (RESTful API)
api = Api(app) 

# create a request parser object that automatically parses the request such that it fits the format/structure
video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Name of the video", required=True)
video_put_args.add_argument("views", type=int, help="Views of the video", required=True)
video_put_args.add_argument("likes", type=int, help="Likes on the video", required=True)

videos ={}

def abort_video_doesnt_exist(video_id):
    if video_id not in videos:
        abort(404, message = "Could not find video...")

def abort_video_exists(video_id):
    if video_id in videos:
        abort(409, message = "Video already exists..")

# make a class that is a resource, and this resource will
# have methods we can override that we can use to handle requests
class Video(Resource):
    def get(self, video_id):
        abort_video_doesnt_exist(video_id)
        return videos[video_id]
    
    def post(self, video_id):
        abort_video_exists(video_id)
        args = video_put_args.parse_args()  # parse the arguments
        videos[video_id] = args             # add the args to the dictionary (1 record)
        return videos[video_id], 201        # return the added argument
    
    def delete(self, video_id):
        abort_video_doesnt_exist(video_id)
        del videos[video_id]
        return '', 204
    
# <> defines the parameter you want to pass in
api.add_resource(Video, "/video/<int:video_id>")

if __name__ == "__main__":
    app.run(debug=True)