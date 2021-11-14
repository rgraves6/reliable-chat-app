#!/usr/bin/env python3
# https://dev.to/zeyu2001/build-a-chatroom-app-with-python-44fa
import threading
import socket
import argparse
import os

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
        self.client_name = ""

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(1)
        while True:
            client_socket, client_address = sock.accept()
            server_socket = ServerSocket(client_socket, client_address, self)
            server_socket.start()
            self.connections.append(server_socket)

    def broadcast(self, message, source):
        for connection in self.connections:
            if connection.client_address != source:
                connection.send(message)

    def unicast(self, message, destination):
        for connection in self.connections:
            if connection.client_name == destination:
                connection.send(message)

    def remove_connection(self, connection):
        self.connections.remove(connection)


class ServerSocket(threading.Thread):
    def __init__(self, client_socket, client_address, server):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.server = server
        self.client_name = self.client_socket.recv(1024).decode('ascii')
        for client in server.connections:
            if client.client_name == self.client_name:
                self.client_socket.send(('{}\n'.format('Username is taken. Please choose another')).encode('ascii'))
                self.client_socket.close()
        self.client_socket.send(('{}\n'.format('Available Clients:')).encode('ascii'))
        for client in server.connections:
            if client.client_name != self.client_name:
                self.client_socket.send(('{}\n'.format(client.client_name)).encode('ascii'))

    def run(self):
        while True:
            message = self.client_socket.recv(1024).decode('ascii')
            if message:
                if message.startswith('@'):
                    destination = message.split()[0]
                    destination = destination.replace('@', "")
                    unicast_message = '{}: {}'.format(self.client_name, message)
                    self.server.unicast(unicast_message, destination)
                else:
                    broadcast_message = '{}: {}'.format(self.client_name, message)
                    self.server.broadcast(broadcast_message, self.client_address)
            else:
                print('{} has closed the connection'.format(self.client_address))
                self.client_socket.close()
                self.server.remove_connection(self)
                return

    def send(self, message):
        self.client_socket.sendall(message.encode('ascii'))


def exit(server):
    while True:
        ipt = input('')
        if ipt == '.quit':
            for connection in server.connections:
                connection.client_socket.close()
            os._exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reliable Chat Server')
    parser.add_argument('--host', type=str, default='localhost', help='Server Hostname')
    parser.add_argument('--port', type=int, default=8080, help='Server Port Number (default 8080)')
    args = parser.parse_args()
    server = Server(args.host, args.port)
    server.start()
    exit = threading.Thread(target=exit, args=(server,))
    exit.start()
