from threading import Thread, Lock
import socket
import struct

import cv2
import numpy as np

def bytes2int(data):
    return int.from_bytes(data, byteorder='little')

class Queue:
    def __init__(self, max_length):
        self.data = []
        self.max_length = max_length
        self.mutex = Lock()
    def push(self, item):
        self.mutex.acquire()
        self.data.append(item)
        while len(self.data) > self.max_length:
            del self.data[0]
        self.mutex.release()
    def read(self):
        self.mutex.acquire()
        data = self.data
        self.mutex.release()
        return data

class UdpServer:
    def __init__(self, host, port):
        self.frame_queue = Queue(1)
        self.head = 0xAAAA
        self.tail = 0xDDDD
        self.udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.send_mutex = Lock()
        self.udp_server.bind((host, port))
        self.udp_server.setblocking(False)
        self.client_address = None
        self.recv_thread = Thread(target=self.recv_loop)
        self.recv_thread.start()
    def close(self):
        self.udp_server.close()
        self.recv_thread.join()
        return
    def send_msg(self, buf, length, msg_type):
        self.send_mutex.acquire()
        if self.client_address is None:
            return
        msg_type = bytes([msg_type])
        data = struct.pack("<HcH", self.head, msg_type, length) + buf + struct.pack("<H", self.tail)
        self.udp_server.sendto(data, self.client_address)
        self.send_mutex.release()
    def recv_loop(self):
        while True:
            try:
                (packet, address) = self.udp_server.recvfrom(10000)
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
                if not address == self.client_address:
                    self.client_address = address
                    print("[LOGGING]: client {}".format(address))
                if msg_type == 1:
                    frame = cv2.imdecode(np.fromstring(buf, dtype=np.uint8), -1)
                    #print( length )
                    if frame is not None:
                        self.frame_queue.push(frame)
                    else:
                        print("img decode error")
            except (IndexError, AssertionError):
                print("msg ")
                continue