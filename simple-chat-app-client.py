#!/usr/bin/env python3
# https://dev.to/zeyu2001/build-a-chatroom-app-with-python-44fa
import threading
import socket
import argparse
import os


class Send(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        while True:
            message = input('{}: '.format(self.name))
            if message == '.exit':
                self.sock.sendall('Server: {} has left the chat.'.format(self.name).encode('ascii'))
                break
            else:
                self.sock.sendall('{}'.format(message).encode('ascii'))
        self.sock.close()
        os._exit(0)


class Receive(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        while True:
            message = self.sock.recv(1024)
            if message:
                print('\r{}\n{}: '.format(message.decode('ascii'), self.name), end='')
            else:
                self.sock.close()
                os._exit(0)


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.sock.connect((self.host, self.port))
        name = input('Your name: ')
        self.sock.sendall(name.encode('ascii'))
        send = Send(self.sock, name)
        receive = Receive(self.sock, name)
        send.start()
        receive.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reliable Chat Client')
    parser.add_argument('--host', type=str, default='localhost', help='Server Hostname')
    parser.add_argument('--port', type=int, default=8080, help='Server Port Number (default 8080)')
    args = parser.parse_args()

client = Client(args.host, args.port)
client.start()
