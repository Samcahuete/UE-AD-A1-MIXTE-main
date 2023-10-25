from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

# CALLING gRPC requests
import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc

# CALLING GraphQL requests

def get_bookings_by_userid(stub, userid):
   bookings = stub.GetBookingsByUserId(userid)
   print(userid)
   for booking in bookings :
      print(booking)

def add_bookingData_by_userid(stub, movieSchedule_with_userid):
    print("c'est super")
    print(stub.addBooking(movieSchedule_with_userid))


def run():
   with grpc.insecure_channel('localhost:3001') as channel:
      stub = booking_pb2_grpc.BookingStub(channel)

      print("-------------- GetBookingsByUserId --------------")
      userid = booking_pb2.UserId(userid="dwight_schrute")
      get_bookings_by_userid(stub, userid)
      ##remplacer date par 20151202 pour vérifier la fonctionnalité de validité des schedules
      mock_movieSchedule = booking_pb2.MovieSchedule(date = "20151202", movieid = "276c79ec-a26a-40a6-b3d3-fb242a5947b6")
      print("mock_movieSchedule ", mock_movieSchedule)
      mock_userid = booking_pb2.UserId(userid="helene_coullon")
      mock_movieSchedule_with_userid = booking_pb2.MovieScheduleWithUserId(userid = mock_userid, movieSchedule = mock_movieSchedule)
      print("mock_movieSchedule_with_userid ", mock_movieSchedule_with_userid)
      add_bookingData_by_userid(stub, mock_movieSchedule_with_userid)

      channel.close()

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/data/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
   return make_response("<h1 style='color:blue'>Welcome to the User service!</h1>", 200)

@app.route("/users", methods=['GET'])
def get_json():
    res = make_response(jsonify(users), 200)
    return res

@app.route("/users/<userid>", methods=['GET'])
def get_user_by_id(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user),200)
            return res
    return make_response(jsonify({"error":"bad input parameter"}),400)

def get_bookings_by_userid_REST(userid):
    bookings = requests.get('http://localhost:3201/bookings/'+userid).json()
    res = make_response(jsonify(bookings["dates"]),200)
    return res

@app.route("/users/movies/<userid>", methods=['GET'])
def get_movies_by_userid(userid):
    user_bookings_request = requests.get('http://localhost:3203/users/bookings/'+userid)
    user_bookings = user_bookings_request.json()
    if user_bookings_request.status_code == 200:
        moviesInfo = {
            "movies":[]
        }
        for booking in user_bookings:
            for movieid in booking["movies"]:
                movie_request = requests.get('http://localhost:3200/movies/'+movieid)
                movie = movie_request.json()
                if movie_request.status_code ==200:
                    moviesInfo["movies"].append(movie)
        return make_response(jsonify(moviesInfo),200)
    return make_response(jsonify({"error": "no booking found for user" + userid}), 400)

if __name__ == "__main__":
   run()
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)

