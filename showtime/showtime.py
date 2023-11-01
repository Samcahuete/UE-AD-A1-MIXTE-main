import grpc
from concurrent import futures
import showtime_pb2
import showtime_pb2_grpc
import json

class ShowtimeServicer(showtime_pb2_grpc.ShowtimeServicer):

    def __init__(self):
        with open('{}/data/times.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["schedule"]

    def GetScheduleByDate(self, request, context):
        """
        Retrieves schedules thanks to the requested date
        :param request: {Date}
        :param context:
        :return: {ScheduleData}
        """
        # Goes through all the schedules
        for schedule in self.db:
            # Verifies if it matches the requested date
            if schedule['date'] == request.date:
                print("Schedule found!")
                return showtime_pb2.ScheduleData(date=schedule['date'], movies=schedule['movies'])
        print("Schedule not found")
        # returns an empty ScheduleDate
        return showtime_pb2.ScheduleData(date="", movies=[])

    def GetAllSchedules(self, request, context):
        """
        Retrieves all schedules
        :param request: {EmptyDate}
        :param context:
        :yield: ScheduleDate
        """
        # Goes through all the bookings
        for schedule in self.db:
            # yields schedule
            yield showtime_pb2.ScheduleData(date=schedule['date'], movies=schedule['movies'])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    showtime_pb2_grpc.add_ShowtimeServicer_to_server(ShowtimeServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
