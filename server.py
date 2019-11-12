import sys
import os
import csv
from threading import Thread, Lock
import socket
import struct
from datetime import datetime
import configparser
from collections import deque
import cv2
import numpy as np


CONFIG_FILE = "ground_control.cfg"
if not os.path.exists(os.path.join(os.getcwd(), CONFIG_FILE)):
    print("[ERROR]: no gound_control.cfg found")
    sys.exit()
CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_FILE)
IMG_MSG = CONFIG.getint("MSG_TYPE", "IMG_MSG")
POSITION_NED_MSG = CONFIG.getint("MSG_TYPE", "POSITION_NED_MSG")
VELOCITY_BODY_MSG = CONFIG.getint("MSG_TYPE", "VELOCITY_BODY_MSG")
ATTITUDE_MSG = CONFIG.getint("MSG_TYPE", "ATTITUDE_MSG")
VEHICLE_STATUS_MSG = CONFIG.getint("MSG_TYPE", "VEHICLE_STATUS_MSG")
INPUT_ALTITUDE_MSG = CONFIG.getint("MSG_TYPE", "INPUT_ALTITUDE_MSG")
LOG_MSG = CONFIG.getint("MSG_TYPE", "LOG_MSG")

def bytes2int(data):
    return int.from_bytes(data, byteorder='little')

class Queue:
    def __init__(self, max_length):
        self.data = deque(maxlen=max_length)
        self.mutex = Lock()
    def push(self, item):
        self.mutex.acquire()
        self.data.append(item)
        self.mutex.release()
    def read(self):
        self.mutex.acquire()
        data = self.data.copy()
        self.mutex.release()
        return data
    def clear(self):
        self.mutex.acquire()
        self.data.clear()
        self.mutex.release()

class UdpServer:
    def __init__(self, host, port):
        self.frame_queue = Queue(1)
        self.position_queue = Queue(300)
        self.velocity_queue = Queue(300)
        self.attitude_queue = Queue(300)
        self.vehicle_status_queue = Queue(1)
        self.input_attitude_queue = Queue(500)
        self.reference_down_queue = Queue(500)
        self.reference_ne_queue = Queue(500)
        self.target_queue = Queue(100)
        self.control_status_queue = Queue(1)
        self.log_queue = Queue(10)
        self.head = 0xAAAA
        self.tail = 0xDDDD
        self.udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_address_mutex = Lock()
        self.udp_server.bind((host, port))
        self.udp_server.setblocking(False)
        self.client_address = None
        self.recv_thread = Thread(target=self.recv_loop)
        self.recv_thread.start()
        self.csv_file = open("log/" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ".csv", "w")
        self.log_file = csv.writer(self.csv_file, delimiter=',')
    def close(self):
        self.udp_server.close()
        self.recv_thread.join()
        self.csv_file.close()
        return
    def send_msg(self, buf, length, msg_type):
        self.client_address_mutex.acquire()
        client_address = self.client_address
        self.client_address_mutex.release()
        if client_address is None:
            return
        msg_type = bytes([msg_type])
        data = struct.pack("<HcH", self.head, msg_type, length) + buf + struct.pack("<H", self.tail)
        self.udp_server.sendto(data, client_address)
    def recv_loop(self):
        while True:
            try:
                (packet, address) = self.udp_server.recvfrom(0xFFFF)
            except socket.error as error:
                if error.errno == 11:
                    continue
                print(error)
                return
            if packet == b'':
                print("[WARNING]: remote closed")
                continue
            try:
                assert bytes2int(packet[0:2]) == 0xAAAA
                msg_type = bytes2int(packet[2:3])
                length = bytes2int(packet[3:5])
                buf = packet[5:5+length]
                assert bytes2int(packet[5+length:]) == 0xDDDD
                self.client_address_mutex.acquire()
                if not address == self.client_address:
                    self.client_address = address
                    print("[LOGGING]: client {}".format(address))
                self.client_address_mutex.release()
                if msg_type == IMG_MSG:
                    frame = cv2.imdecode(np.fromstring(buf, dtype=np.uint8), -1)
                    #print( length )
                    if frame is not None:
                        self.frame_queue.push(frame)
                    else:
                        print("img decode error")
                    continue
                if msg_type == POSITION_NED_MSG:
                    assert(length % 24 == 0)
                    position_vec = struct.iter_unpack("<qfff4x", buf)
                    for position in position_vec:
                        #print(position)
                        self.position_queue.push(position)
                        self.log_file.writerow(["PositionNED"] + list(position))
                    continue
                if msg_type == VELOCITY_BODY_MSG:
                    assert(length % 24 == 0)
                    velocity_vec = struct.iter_unpack("<qfff4x", buf)
                    for velocity in velocity_vec:
                        #print(velocity)
                        self.velocity_queue.push(velocity)
                        self.log_file.writerow(["VelocityBody"] + list(velocity))
                    continue
                if msg_type == ATTITUDE_MSG:
                    assert(length % 24 == 0)
                    attitude_vec = struct.iter_unpack("<qfff4x", buf)
                    for attitude in attitude_vec:
                        #print(attitude)
                        self.attitude_queue.push(attitude)
                        self.log_file.writerow(["EulerAngle"] + list(attitude))
                if msg_type == VEHICLE_STATUS_MSG:
                    assert(length % 80 == 0 )
                    status_vec = struct.iter_unpack("<q????fff50s6x", buf)
                    for status in status_vec:
                        self.vehicle_status_queue.push(status)
                if msg_type == INPUT_ALTITUDE_MSG:
                    assert(length % 24 == 0)
                    input_attitude_vec = struct.iter_unpack("<qffff", buf)
                    for input_attitude in input_attitude_vec:
                        self.input_attitude_queue.push(input_attitude)
                        self.log_file.writerow(["InputAttitude"] + list(input_attitude))
                if msg_type == 10:
                    assert(length % 16 == 0)
                    reference_ne_vec = struct.iter_unpack("<qff", buf)
                    for reference_ne in reference_ne_vec:
                        self.reference_ne_queue.push(reference_ne)
                        self.log_file.writerow(["ReferenceNE"] + list(reference_ne))
                if msg_type == LOG_MSG:
                    log = struct.unpack("{}s".format(length), buf)[0]
                    self.log_queue.push(log)
                if msg_type == 8:
                    assert(length % 16 == 0)
                    reference_vec = struct.iter_unpack("<qf4x", buf)
                    for reference in reference_vec:
                        self.reference_down_queue.push(reference)
                        self.log_file.writerow(["ReferenceDown"] + list(reference))
                if msg_type == 9:
                    assert(length % 32 == 0)
                    target_vec = struct.iter_unpack("qifffff", buf)
                    for target in target_vec:
                        self.target_queue.push(target)
                        self.log_file.writerow(["Target"] + list(target))
                if msg_type == 11:
                    assert(length % 16 == 0)
                    control_status_vec = struct.iter_unpack("<qh6x", buf)
                    for status in control_status_vec:
                        self.log_file.writerow(["ControlStatus"] + list(status))
                        self.control_status_queue.push(status)
                if msg_type == 21:
                    assert(length % 16 == 0)
                    err_xy_vec = struct.iter_unpack("<qff", buf)
                    for err in err_xy_vec:
                        self.log_file.writerow(["PosXYErr"] + list(err))
            except (IndexError, AssertionError):
                print("msg broken")
                continue
