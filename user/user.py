from flask import Flask, request, jsonify, make_response
import requests
import json

# CALLING gRPC requests
import grpc
import booking_pb2
import booking_pb2_grpc

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

""" We load the database """
with open('{}/data/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]


def update_db(users_db):
    """
        Returns the users database updated
        param : the database to update
        return : the database on a json format
    """
    with open('{}/data/users.json'.format("."), "w") as wfile:
        formatted_users = {
            "users": users_db
        }
        json.dump(formatted_users, wfile)
    return users_db


def get_bookings_by_userid(stub, userid):
    """ Calls the booking service to retrieve the bookings of the user using its userid
    :param stub: booking_pb2_grpc.BookingStub
    :param userid: booking_pb2.UserId
    return: [BookingData]
    """
    return stub.GetBookingsByUserId(userid)


def add_bookingData_by_userid(stub, movieSchedule_with_userid):
    """ Add a booking to a user by calling the booking service.
    If the user has no booking registered, it creates a new element in the booking database using the userid.
    If the user is not found in the user database, we create a new user
    :param stub: booking_pb2_grpc.BookingStub
    :param movieSchedule_with_userid: booking_pb2.MovieScheduleWithUserId
    :return: booking_pb2.MovieScheduleWithUserId
    """
    return stub.addBooking(movieSchedule_with_userid)


def delete_bookingData_by_userid(stub, movieSchedule_with_userid):
    """ Add a booking to a user by calling the booking service.
    If the user has no booking registered, it creates a new element in the booking database using the userid.
    If the user is not found in the user database, we create a new user
    :param stub: booking_pb2_grpc.BookingStub
    :param movieSchedule_with_userid: booking_pb2.MovieScheduleWithUserId
    :return: booking_pb2.MovieScheduleWithUserId
    """
    return stub.deleteBooking(movieSchedule_with_userid)


@app.route("/", methods=['GET'])
def home():
    """
    Homepage
    """
    return make_response("<h1 style='color:blue'>Welcome to the User service!</h1>", 200)


@app.route("/users", methods=['GET'])
def get_json():
    """
    Retrieve all the users registered in the database
    :return: Response
    """
    res = make_response(jsonify(users), 200)
    return res


@app.route("/users/<userid>", methods=['GET'])
def get_user_by_id(userid):
    """
    Retrieve the user associated with the requested userid
    :param userid: string
    :return: Response
    """
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user), 200)
            return res
    return make_response(jsonify({"error": "bad input parameter"}), 400)

@app.route("/users/<userid>", methods=['POST'])
def add_user(userid):
    """
        Add a user to the database if it doesn't already exist
        param : a string userid
    """
    # retrieves the user data
    user_req = request.get_json()
    # verifies if the request is coherent
    if user_req["id"]   != userid:
        res = make_response(jsonify({"error": f"the userid specified in the url ({userid}) "
                                              f"doesn't match with the one given in the body ({user_req['id']})"}), 400)
        return res
    # verifies if the user already exists
    for user in users:
        if user["id"] == userid:
            res = make_response(jsonify({"error": f"user {userid} already exists"}), 400)
            return res
    # updates the database
    users.append(user_req)
    update_db(users)
    return make_response(jsonify({"message": f"user {userid} added"}), 200)

@app.route("/users/<userid>", methods=['DELETE'])
def delete_user(userid):
    """
        Delete a user given its id and all its bookings
        param : a string userid
    """
    # Opens a new channel with the booking service to retrieve the bookings of the user
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)
        requested_userid = booking_pb2.UserId(userid=userid)
        # Deletes all the bookings of the user
        stub.deleteAllBooking(requested_userid)
        channel.close()
    # goes through all the users to find the requested user
    for user in users:
        if user["id"] == userid:
            # removes the user and updates the database
            users.remove(user)
            update_db(users)
            res = make_response(jsonify({"message": f"user {userid} deleted"}), 200)
            return res
    # user non exist
    return make_response(jsonify({"error": f"non existent user {userid}"}), 400)


@app.route("/users/bookings/<userid>", methods=['GET'])
def get_bookings_by_userid(userid):
    """
        Returns the bookings of a user from the booking database knowing the userid
        param : a string userid
        return : the bookings requested in json format
    """
    bookings = []
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)
        requested_userid = booking_pb2.UserId(userid=userid)
        # Gets the bookings of the user
        bookings_stream = stub.GetBookingsByUserId(requested_userid)
        # the response is a stream, as well as its movies
        for user_bookings in bookings_stream:
            bookings.append({
            "date": user_bookings.date,
            "movies": [movie for movie in user_bookings.movies]
        })
        channel.close()
    res = make_response(jsonify(bookings), 200)
    return res


@app.route("/users/movies/<userid>", methods=['GET'])
def get_movies_by_userid(userid):
    """
    Retrieve the information about all the movies booked by the user.
    :param userid: string
    :return: Response
    """
    # Opens a new channel with the booking service to retrieve the bookings of the user
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)
        requested_userid = booking_pb2.UserId(userid=userid)
        # We request the booking service and retrieve a stream of data
        user_bookings_stream = stub.GetBookingsByUserId(requested_userid)
        # We collect the data of the stream
        user_bookings = []
        for booking in user_bookings_stream:
            user_bookings.append(booking)
        # We close the channel
        channel.close()
    # We verify if we found registered bookings for the user
    if user_bookings is not None:
        # This object will be used to store the movies found
        moviesInfo = {
            "movies": []
        }
        # We go through all the movies of all the bookings of the user
        for booking in user_bookings:
            for movieid in booking.movies:
                # Creates the graphql query
                query_content = """
{
  movie_with_id(_id: %s) {
    id
    title
    rating
    director
    actors {
      firstname
      lastname
      birthyear
    }
  }
}
""" % ('"' + movieid + '"')
                # Final format of the body request
                query = {'query': query_content}
                # We call the movie service with the previous graphql query
                movie_request = requests.post('http://localhost:3003/graphql', json=query)
                # We verify if the request was successful
                if movie_request.status_code == 200:
                    # We retrieve the movie as a json
                    movie = movie_request.json()
                    # We add the movie info to the response content
                    moviesInfo["movies"].append(movie)
        # We create the response with the retrieved movies
        return make_response(jsonify(moviesInfo), 200)
    # If no booking is found for the user we return an error status
    return make_response(jsonify({"error": "no booking found for user " + userid}), 400)


if __name__ == "__main__":
    # tests for the booking service
    print("Server running in port %s" % PORT)
    app.run(host=HOST, port=PORT)
