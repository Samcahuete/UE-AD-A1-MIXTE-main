# REST API
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

def run():
   with grpc.insecure_channel('localhost:3002') as channel:
      stub = booking_pb2_grpc.BookingStub(channel)

      print("-------------- GetBookingsByUserId --------------")
      userid = booking_pb2.UserId(userid="dwight_schrute")
      get_bookings_by_userid(stub, userid)


app = Flask(__name__)

PORT = 3004
HOST = '0.0.0.0'

with open('{}/data/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

if __name__ == "__main__":
   run()
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)

