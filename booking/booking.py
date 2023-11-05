import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc
import json
import requests


class BookingServicer(booking_pb2_grpc.BookingServicer):
    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def updateDB(self, bookings):
        """
        Updates the json file containing the bookings data
        :param bookings: [Booking]
        :return: [Booking]
        """
        with open('{}/data/bookings.json'.format("."), "w") as wfile:
            formatted_bookings = {
                "bookings": bookings
            }
            json.dump(formatted_bookings, wfile)
        return bookings

    def GetBookingsByUserId(self, request, context):
        """
        Retrieves bookings for the requested user
        :param request: {userid}
        :param context:
        :yield: Booking
        """
        # We go through all the bookings
        for booking in self.db:
            # We verify if the userid matches with the requested userid
            if booking["userid"] == request.userid:
                print("User found !")
                # Yields all the registered schedules
                for date in booking["dates"]:
                    yield booking_pb2.BookingData(date=date["date"], movies=date["movies"])
        print("user booking not found")
        # We yield nothing in the stream of data
        yield None

    def checkBookingValidity(self, request, context):
        """
        Verify if the movie schedule is registered in the showtime database
        :param request: {date, movieid}
        :param context:
        :return: Validity = {validity:bool}
        """
        # Extraction of the request data
        new_movie_date = request.date
        new_movieid = request.movieid
        # New channel with the showtime service to verify the validity of the schedule
        with grpc.insecure_channel('localhost:3002') as channel:
            stub = showtime_pb2_grpc.ShowtimeStub(channel)
            date = showtime_pb2.Date(date = new_movie_date)
            check_date_existence = stub.GetScheduleByDate(date)
            if check_date_existence.date == "":
                print("The requested schedule is not valid according to the showtime service")
                channel.close()
                return booking_pb2.Validity(validity=False)
            available_movies = check_date_existence.movies
            if new_movieid in available_movies:
                print("The requested schedule is valid")
                channel.close()
                return booking_pb2.Validity(validity=True)
            print("The requested schedule is not valid according to the showtime service")
            # We close the channel
            channel.close()
            return booking_pb2.Validity(validity=False)

    def addBooking(self, request, context):
        """
        Add the requested schedule to the booking database.
        If the user is not found, we create a new user with the booking
        :param request: {userid, movieSchedule}
        :param context:
        :return: {userid, movieSchedule}
        """
        # We extract the request data
        userid = request.userid.userid
        movieSchedule = request.movieSchedule
        # We first check the validity of the schedule
        validity = self.checkBookingValidity(movieSchedule, context).validity
        print("oui")
        user_existence_response = requests.get(f'http://localhost:3203/users/{userid}')
        print("user_existence_response", user_existence_response)
        if not validity:
            print("The schedule requested isn't available; please verify the schedule requested")
            return request
        if user_existence_response.status_code != 200:
            print("error: user not found")
            return request
        # We go through all the bookings to match the userid, schedules date and schedules movieid
        # Depending on the match result, we have to either create a new user,
        # create a new schedule date or update the movies list stored in the "dates" field
        # Finally, if the schedule already exists in the database we do nothing
        for booking in self.db:
            if booking["userid"] == userid:
                print("user found")
                for schedule in booking["dates"]:
                    if schedule["date"] == movieSchedule.date:
                        print("date found")
                        for movie in schedule["movies"]:
                            if movie == movieSchedule.movieid:
                                # The schedule is found in the database, we stop the process
                                print(f"error: booking already registered for user {userid}")
                                return request
                        # The date is found, we update the movies list in the database
                        schedule["movies"].append(movieSchedule.movieid)
                        bookings = self.db
                        self.updateDB(bookings)
                        print("Booking added")
                        return request
                # The user is found but not the date, therefore we create a new date and update the database
                print(f"date not found for the user {userid}")
                new_date = {
                    "date": movieSchedule.date,
                    "movies": [movieSchedule.movieid]
                }
                booking["dates"].append(new_date)
                bookings = self.db
                self.updateDB(bookings)
                print("Booking added")
                return request
        # The user is not found, we create a new booking with the userid
        print("user not found")
        new_date = {
            "date": movieSchedule.date,
            "movies": [movieSchedule.movieid]
        }
        new_user_booking = {
            "dates": [new_date],
            "userid": userid
        }
        self.db.append(new_user_booking)
        bookings = self.db
        self.updateDB(bookings)
        print("Booking created")
        return request

    def deleteBooking(self, request, context):
        """
        Delete the requested booking.
        If there is no matching with any registered booking, does nothing
        :param request: {userid, movieSchedule}
        :param context:
        :return: {userid, movieSchedule}
        """
        # We extract the request data
        userid = request.userid.userid
        movieSchedule = request.movieSchedule
        # We first verify if there is a match with one of the registered booking
        for booking in self.db:
            if booking["userid"] == userid:
                print("user found")
                for schedule in booking["dates"]:
                    if schedule["date"] == movieSchedule.date:
                        print("date found")
                        for movie in schedule["movies"]:
                            if movie == movieSchedule.movieid:
                                print("booking found")
                                # We delete the movie from the movies list
                                schedule["movies"].remove(movieSchedule.movieid)
                                # If the new movies list is now empty, we need to remove it
                                if len(schedule["movies"]) == 0:
                                    booking["dates"].remove(schedule)
                                    # if the "dates" list is now empty, we need to remove the bookings
                                    if len(booking["dates"]) == 0:
                                        self.db.remove(booking)
                                # We update the database
                                bookings = self.db
                                self.updateDB(bookings)
                                print("booking deleted")
                                return request
        # No booking found, we do nothing
        print(f"booking not found for user {userid}")
        return request


    def deleteAllBooking(self, request, context):
        """
        Delete all the bookings of the given user (id) from the bookings database
        :param request: UserId
        :param context:
        :return: {userid, movieSchedule}
        """
        # We extract the request data
        userid = request.userid
        for user_bookings in self.db:
            if user_bookings["userid"] == userid:
                self.db.remove(user_bookings)
                self.updateDB(self.db)
                print("bookings found and deleted")
                return request
        print("No booking found")
        return request


def get_schedule_by_date(stub, date):
    """
    Retrieved schedule thanks to date
    :param date: Date
    :return:
    """
    #Calls the showtime service
    schedule = stub.GetScheduleByDate(date)
    print(f"schedule: \n {schedule}")
    return schedule;


def get_all_schedules(stub):
    """
    Retrieves all schedules
    :param stub:
    :return:
    """
    #the showtime service requires an EmptyDate in the request
    empty_date = showtime_pb2.EmptyDate()
    #Calls the showtime service
    all_schedules = stub.GetAllSchedules(empty_date)
    #the following print should show that we receive a stream of data
    print("all_schedules", all_schedules)
    return all_schedules


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3001')
    server.start()
    server.wait_for_termination()





if __name__ == '__main__':
    serve()
