import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc
import json

class BookingServicer(booking_pb2_grpc.BookingServicer):
    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def updateDB(self, bookings):
        with open('{}/data/bookings.json'.format("."), "w") as wfile:
            formatted_bookings = {
                "bookings": bookings
            }
            json.dump(formatted_bookings, wfile)
        return bookings
    def GetBookingsByUserId(self, request, context):
        print("oui")
        for booking in self.db:
            print("booking", booking)
            if booking["userid"] == request.userid:
                print("User found !")
                for date in booking["dates"] :
                    yield booking_pb2.BookingData(date=date["date"], movies=date["movies"])

    def checkBookingValidity(self, request, context):
        print("request", request)
        new_movie_date = request.date
        new_movieid = request.movieid

        with grpc.insecure_channel('localhost:3002') as channel:
            stub = showtime_pb2_grpc.ShowtimeStub(channel)
            all_schedules = get_all_schedules(stub)


            print("allschedules", all_schedules)
            for element in all_schedules:
                print("element", element)
                if element.date == new_movie_date:
                    print("element.date",element.date)
                    for movie in element.movies:
                        print("movie", movie)
                        if movie == new_movieid:
                            print("ah ouai c'est bon")
                            channel.close()
                            return booking_pb2.Validity(validity = True)
            print("ah non c'est pas bon")
            channel.close()
            return booking_pb2.Validity(validity = False)

    def addBooking(self, request, context):
        userid = request.userid.userid
        movieSchedule = request.movieSchedule
        validity = self.checkBookingValidity(movieSchedule, context).validity
        if not validity:
            print("The schedule requested isn't available; please verify the schedule requested")
            return request
        for booking in self.db:
            print("booking['userid']", booking["userid"])
            print("userid", userid)
            if booking["userid"] == userid:
                print("user found")
                for schedule in booking["dates"]:
                    print("schedule", schedule)
                    if schedule["date"]==movieSchedule.date:
                        print("date found")
                        for movie in schedule["movies"]:
                            if movie == movieSchedule.movieid:
                                print(f"error: booking already registered for user {userid}")
                        schedule["movies"].append(movieSchedule.movieid)
                        bookings = self.db
                        self.updateDB(bookings)
                        return request
                print("date not found")
                new_date = {
                    "date": movieSchedule.date,
                    "movies": [movieSchedule.movieid]
                }
                booking["dates"].append(new_date)
                bookings = self.db
                self.updateDB(bookings)
                return request
        print("user not found")
        new_date = {
            "date": movieSchedule.date,
            "movies": [movieSchedule.movieid]
        }
        new_user_booking = {
            "dates" : [new_date],
            "userid": userid
        }
        self.db.append(new_user_booking)
        bookings = self.db
        self.updateDB(bookings)
        return request

def get_schedule_by_date(stub,date):
    schedule = stub.GetScheduleByDate(date)
    print(schedule)

def get_all_schedules(stub):
    emptyDate = showtime_pb2.EmptyDate()
    all_schedules = stub.GetAllSchedules(emptyDate)
    print("all_schedules", all_schedules)

    return all_schedules

def serve():
     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
     booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
     server.add_insecure_port('[::]:3001')
     server.start()
     server.wait_for_termination()

def run():
    print("aaaaaaaaa")
    with grpc.insecure_channel('localhost:3002') as channel:
        stub = showtime_pb2_grpc.ShowtimeStub(channel)

        print("-------------- GetScheduleByDate --------------")
        date = showtime_pb2.Date(date="20151130")
        get_schedule_by_date(stub, date)
        print("bbbbbbb")
        get_all_schedules(stub)
        channel.close()



if __name__ == '__main__':
    ##run()
    serve()

