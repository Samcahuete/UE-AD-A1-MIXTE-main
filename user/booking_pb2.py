# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: booking.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rbooking.proto\"\x18\n\x06UserId\x12\x0e\n\x06userid\x18\x01 \x01(\t\"+\n\x0b\x42ookingData\x12\x0c\n\x04\x64\x61te\x18\x01 \x01(\t\x12\x0e\n\x06movies\x18\x02 \x03(\t2;\n\x07\x42ooking\x12\x30\n\x13GetBookingsByUserId\x12\x07.UserId\x1a\x0c.BookingData\"\x00\x30\x01\x62\x06proto3')



_USERID = DESCRIPTOR.message_types_by_name['UserId']
_BOOKINGDATA = DESCRIPTOR.message_types_by_name['BookingData']
UserId = _reflection.GeneratedProtocolMessageType('UserId', (_message.Message,), {
  'DESCRIPTOR' : _USERID,
  '__module__' : 'booking_pb2'
  # @@protoc_insertion_point(class_scope:UserId)
  })
_sym_db.RegisterMessage(UserId)

BookingData = _reflection.GeneratedProtocolMessageType('BookingData', (_message.Message,), {
  'DESCRIPTOR' : _BOOKINGDATA,
  '__module__' : 'booking_pb2'
  # @@protoc_insertion_point(class_scope:BookingData)
  })
_sym_db.RegisterMessage(BookingData)

_BOOKING = DESCRIPTOR.services_by_name['Booking']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _USERID._serialized_start=17
  _USERID._serialized_end=41
  _BOOKINGDATA._serialized_start=43
  _BOOKINGDATA._serialized_end=86
  _BOOKING._serialized_start=88
  _BOOKING._serialized_end=147
# @@protoc_insertion_point(module_scope)
