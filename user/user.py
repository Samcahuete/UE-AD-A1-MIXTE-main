from flask import Flask, jsonify, make_response
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


def run():
    """
    Function used to test the booking service implemented with grpc
    It is called at the very beginning of the file execution
    """
    # We open a channel connected to the booking service
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)

        print("-------------- checkBookingValidity --------------")
        mock_movieSchedule = booking_pb2.MovieSchedule(date="20151202", movieid="276c79ec-a26a-40a6-b3d3-fb242a5947b6")
        print("The schedule should be valid: ", stub.checkBookingValidity(mock_movieSchedule))
        random_movieSchedule = booking_pb2.MovieSchedule(date="7787", movieid="276c79ec-a26a-40a6-b3d3-random movie")
        print("The schedule should not be valid: ", stub.checkBookingValidity(random_movieSchedule))

        print("-------------- GetBookingsByUserId --------------")
        userid = booking_pb2.UserId(userid="dwight_schrute")
        print("Bookings of user dwight_schrute: ", get_bookings_by_userid(stub, userid))
        bookings_stream = get_bookings_by_userid(stub, userid)
        for booking in bookings_stream:
            print("booking", booking)
        random_userid = booking_pb2.UserId(userid="random_user")
        print("Bookings of user random_user: ", get_bookings_by_userid(stub, random_userid))
        bookings_stream = get_bookings_by_userid(stub, random_userid)
        for booking in bookings_stream:
            print("booking", booking)

        print("-------------- AddBooking --------------")
        mock_userid = booking_pb2.UserId(userid="obiwan_kenobi")
        mock_movieSchedule_with_userid = booking_pb2.MovieScheduleWithUserId(userid=mock_userid,
                                                                             movieSchedule=mock_movieSchedule)
        print("It should add the booking to the database")
        print(add_bookingData_by_userid(stub, mock_movieSchedule_with_userid))
        print("Bookings for user obiwan_kenobi: ", get_bookings_by_userid(stub, mock_userid))
        print("It shouldn't be able to add again the same schedule")
        add_bookingData_by_userid(stub, mock_movieSchedule_with_userid)

        print("-------------- deleteBooking --------------")
        print("It should delete the previous added booking")
        delete_bookingData_by_userid(stub, mock_movieSchedule_with_userid)

        # channel closed
        channel.close()


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
        user_bookings_stream = get_bookings_by_userid(stub, requested_userid)
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
                # We create the graphql query
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
    run()
    print("Server running in port %s" % PORT)
    app.run(host=HOST, port=PORT)
