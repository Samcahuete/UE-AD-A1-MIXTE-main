import grpc
from concurrent import futures
#import booking_pb2
#import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc
import json

#class BookingServicer(booking_pb2_grpc.BookingServicer):

#    def __init__(self):
#        with open('{}/data/bookings.json'.format("."), "r") as jsf:
#            self.db = json.load(jsf)["schedule"]

def get_schedule_by_date(stub,date):
    schedule = stub.GetScheduleByDate(date)
    print(schedule)

# def serve():
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
#     server.add_insecure_port('[::]:3002')
#     server.start()
#     server.wait_for_termination()

def run():
    with grpc.insecure_channel('localhost:3002') as channel:
        stub = showtime_pb2_grpc.ShowtimeStub(channel)

        print("-------------- GetScheduleByDate --------------")
        date = showtime_pb2.Date(date="20151130")
        get_schedule_by_date(stub, date)

if __name__ == '__main__':
    # serve()
    run()
