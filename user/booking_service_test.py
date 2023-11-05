from flask import Flask, request, jsonify, make_response
import requests
import json

# CALLING gRPC requests
import grpc
import booking_pb2
import booking_pb2_grpc


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
        print("user should be not found: ")
        print(add_bookingData_by_userid(stub, mock_movieSchedule_with_userid))

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


if __name__ == "__main__":
    # tests for the booking service
    run()
