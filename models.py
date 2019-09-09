from threading import Thread, Lock
import socket
import sys
if '/opt/ros/kinetic/lib/python2.7/dist-packages' in sys.path:
    sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
import numpy as np
import struct
import time

import fcntl, os

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

'''
class Server:
    def __init__(self, host, port):
        self.start = time.clock()
        self.frame_queue = Queue(1)
        self.state_param_queue = Queue(1)
        self.sensor_data_queue = Queue(200)
        self.visual_data_queue = Queue(200)
        self.run = True
        self.bind_listen(host, port)
        self.accept()
        self.start_recv_thread()
    def restart(self, host, port):
        self.close()
        self.bind_listen(host, port)
        self.accept()
        self.start_recv_thread()
    def bind_listen(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 128*1024*1024)
        self.sock.bind((host, port))
        self.sock.listen()
    def accept(self):
        self.conn, self.addr = self.sock.accept()
    def close(self):
        self.close_recv_thread()
        self.sock.shutdown(2)
        self.recv_thread.join()
        self.sock.close()
    def start_recv_thread(self):
        self.run = True
        self.recv_thread = Thread(target=self.recv_loop)
        self.recv_thread.start()
        return
    def close_recv_thread(self):
        if self.recv_thread.isAlive():
            self.run = False
        return
    def recvall(self, n):
        data = b''
        while len(data) < n:
            packet = self.conn.recv(n - len(data))
            assert packet != b''
            data = data + packet
        return data
    def recv_loop(self):
        while True:
            if not self.run:
                return
            try:
                head = bytes2int(self.recvall(1))
                if head != 0xAA:
                    continue
                timestamp_ms = bytes2int(self.recvall(8))
                msg_type = bytes2int(self.recvall(1))
                length = bytes2int(self.recvall(2))
                buffer = self.recvall(length)
                tail = bytes2int(self.recvall(1))
                if tail != 0xDD:
                    continue
            except AssertionError:
                print("try reconnect")
                try:
                    self.accept()
                    print("new connection established")
                except:
                    print("socket been shutdown")
            if msg_type == 0:
                state_param = struct.unpack("<??", buffer)
                state_param = state_param + (timestamp_ms,)
                self.state_param_queue.push(state_param)
                #print(state_param)
            elif msg_type == 1:
                frame = cv2.imdecode(np.fromstring(buffer, dtype=np.uint8), -1)
                #print( length )
                if frame is not None:
                    self.frame_queue.push(frame)
                else:
                    print("decode error")
            elif msg_type == 2:
                sensor_data = struct.unpack("<5d", buffer)
                sensor_data = sensor_data + (timestamp_ms,)
                self.sensor_data_queue.push(sensor_data)
            elif msg_type == 3:
                visual_data = struct.unpack("<6d", buffer)
                visual_data = visual_data + (timestamp_ms,)
                self.visual_data_queue.push(visual_data)
    def send_msg(self, buffer, length, msg_type):
        head = bytes([0xAA])
        tail = bytes([0xDD])
        msg_type = bytes([msg_type])
        timestamp_ms = int((time.clock() - self.start) * 1000)
        data = struct.pack("<cqch", head, timestamp_ms, msg_type, length) + buffer + struct.pack("<c", tail)
        self.conn.sendall(data)
'''
class UdpServer:
    def __init__(self, host, port):
        self.frame_queue = Queue(1)
        self.state_param_queue = Queue(1)
        self.sensor_data_queue = Queue(200)
        self.visual_data_queue = Queue(200)
        self.udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if fcntl.fcntl(self.udp_server, fcntl.F_SETFL, os.O_RDONLY) < 0:
            print("set udp read only fail")
        self.udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 128*1024*1024)
        self.udp_server.bind((host, port))
        self.recv_thread = Thread(target=self.recv_loop)
        self.recv_thread.start()
    def close(self):
        self.udp_server.close()
        self.recv_thread.join()
        return
    def recvall(self, n):
        data = b''
        while len(data) < n:
            packet = self.udp_server.recv(n - len(data))
            data = data + packet
        return data
    def recv_loop(self):
        try:
            while True:
                head = bytes2int(self.recvall(1))
                if head != 0xAA:
                    continue
                timestamp_ms = bytes2int(self.recvall(8))
                msg_type = bytes2int(self.recvall(1))
                length = bytes2int(self.recvall(2))
                buffer = self.recvall(length)
                tail = bytes2int(self.recvall(1))
                if tail != 0xDD:
                    continue
                if msg_type == 0:
                    state_param = struct.unpack("<??", buffer)
                    state_param = state_param + (timestamp_ms,)
                    self.state_param_queue.push(state_param)
                    #print(state_param)
                elif msg_type == 1:
                    frame = cv2.imdecode(np.fromstring(buffer, dtype=np.uint8), -1)
                    #print( length )
                    if frame is not None:
                        self.frame_queue.push(frame)
                    else:
                        print("decode error")
                elif msg_type == 2:
                    sensor_data = struct.unpack("<5d", buffer)
                    sensor_data = sensor_data + (timestamp_ms,)
                    self.sensor_data_queue.push(sensor_data)
                elif msg_type == 3:
                    visual_data = struct.unpack("<6d", buffer)
                    visual_data = visual_data + (timestamp_ms,)
                    self.visual_data_queue.push(visual_data)
        except socket.error:
            return

class TcpServer:
    def __init__(self, host, port):
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_server.bind((host, port))
        self.tcp_server.listen()
        self.conn, self.addr = self.tcp_server.accept()
        self.conn.setblocking( False )
        self.start = time.clock()
        self.head = bytes([0xAA])
        self.tail = bytes([0xDD])
        self.offline = False
        self.run = True
        self.recv_loop_thread = Thread(target=self.recv_loop)
        self.recv_loop_thread.start()
    def close(self):
        self.tcp_server.shutdown(2)
        self.tcp_server.close()
        self.run = False
        self.recv_loop_thread.join()
    def send_msg(self, buf, length, msg_type):
        if self.offline:
            return
        msg_type = bytes([msg_type])
        timestamp_ms = int((time.clock() - self.start) * 1000)
        data = struct.pack("<cqch", self.head, timestamp_ms, msg_type, length) + buf + struct.pack("<c", self.tail)
        self.conn.sendall(data)
    def recv_loop(self):
        while self.run:
            try:
                if self.conn.recv(1) == b'':
                    self.offline = True
                    print("try reconnect")
                    self.conn, self.addr = self.tcp_server.accept()
                    self.offline = False
                    print("new connection established")
            except socket.error:
                continue

'''
def main():
    host = '127.0.0.1'
    udpserver = UdpServer(host, 8080)
    tcpserver = TcpServer(host, 8080)
    while True:
        frame_queue = udpserver.frame_queue.read()
        if frame_queue != []:
            frame = frame_queue[0]
            cv2.imshow("camera", frame)
            cv2.waitKey(5)
if __name__ == "__main__":
    main()
'''