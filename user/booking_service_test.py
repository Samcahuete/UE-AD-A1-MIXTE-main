from flask import Flask, request, jsonify, make_response
import requests
import json

# CALLING gRPC requests
import grpc
import booking_pb2
import booking_pb2_grpc

mock_movieSchedule = booking_pb2.MovieSchedule(date="20151202", movieid="276c79ec-a26a-40a6-b3d3-fb242a5947b6")
random_movieSchedule = booking_pb2.MovieSchedule(date="7787", movieid="276c79ec-a26a-40a6-b3d3-random movie")

# bizarre: lorsque Validity est à True, le print fonctionne correctement
# quand validity est à False, le print effectue uniquement un retour à la ligne (cela vient sûrement de grpc) :
print("Validity false: ",booking_pb2.Validity(validity=False))
print("Validity true: ",booking_pb2.Validity(validity=True))
def testCheckBookingValidity():
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)
        print("-------------- checkBookingValidity --------------")
        print("The schedule should be valid: ", stub.checkBookingValidity(mock_movieSchedule))
        print("The schedule should not be valid: ", stub.checkBookingValidity(random_movieSchedule))
        channel.close()

if __name__ == "__main__":
    testCheckBookingValidity()


userid = booking_pb2.UserId(userid="dwight_schrute")
random_userid = booking_pb2.UserId(userid="random_user")
def testGetBookingsByUserId():
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)
        print("-------------- getBookingsByUserId --------------")
        print("Bookings of user dwight_schrute: ")
        bookings_stream = stub.GetBookingsByUserId(userid)
        for booking in bookings_stream:
            print("booking", booking)
        print("Bookings of user random_user: ")
        bookings_stream = stub.GetBookingsByUserId(random_userid)
        for booking in bookings_stream:
            print("booking", booking)
        channel.close()

if __name__ == "__main__":
    testGetBookingsByUserId()

mock_userid = booking_pb2.UserId(userid="obiwan_kenobi")
mock_movieSchedule_with_userid = booking_pb2.MovieScheduleWithUserId(userid=mock_userid,
                                                                    movieSchedule=mock_movieSchedule)
mock_movieSchedule_with_userid2 = booking_pb2.MovieScheduleWithUserId(userid=userid,
                                                                    movieSchedule=mock_movieSchedule)
def testAddBooking():
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)
        print("-------------- AddBooking --------------")

        print("user should be not found: ")
        print(stub.addBooking(mock_movieSchedule_with_userid))
        print("It should add the booking to the database")
        print(stub.addBooking(mock_movieSchedule_with_userid2))
        print("Bookings for user dwight_schrute: ", stub.GetBookingsByUserId(userid))
        print("It shouldn't be able to add again the same schedule")
        stub.addBooking(mock_movieSchedule_with_userid2)
        channel.close()

if __name__ == "__main__":
    testAddBooking()

def testDeleteBooking():
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)
        print("-------------- deleteBooking --------------")
        print("It should delete the previous added booking")
        stub.deleteBooking(mock_movieSchedule_with_userid2)
        print("It shouldn't be able to delete again the booking:")
        stub.deleteBooking(mock_movieSchedule_with_userid2)
        channel.close()

if __name__ == "__main__":
    testDeleteBooking()



