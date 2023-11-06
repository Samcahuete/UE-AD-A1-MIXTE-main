import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc
import json
import requests


def test_showtime():
    """
    Tests for the showtime service
    :return:
    """
    # We open a channel connected to the showtime service
    with grpc.insecure_channel('localhost:3002') as channel:
        stub = showtime_pb2_grpc.ShowtimeStub(channel)

        print("-------------- GetAllSchedules --------------")
        print("Should return all the schedules in the times database:")
        all_schedules = get_all_schedules(stub)
        for schedule in all_schedules:
            print(schedule)

        print("-------------- GetScheduleByDate --------------")
        print("       -- A schedule should be found --")
        date = showtime_pb2.Date(date="20151130")
        get_schedule_by_date(stub, date)

        print("       -- No schedule should be found --")
        date = showtime_pb2.Date(date="Unknown date")
        get_schedule_by_date(stub, date)
        channel.close()











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


if __name__ == '__main__':
    test_showtime()


