# Python program to implement server side of chat room.
import socket
# import select
# import sys
import threading
from utils import get_rooms
# '''Replace "thread" with "_thread" for python 3'''
# from _thread import *

"""The first argument AF_INET is the address domain of the
socket. This is used when we have an Internet Domain with
any two hosts The second argument is the type of socket.
SOCK_STREAM means that data or characters are read in
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = "127.0.0.1"  # servidor vai rodar na maquina local
Port = 8080  # porta

"""
binds the server to an entered IP address and at the
specified port number.
The client must be aware of these parameters
"""
server.bind((host, Port))

"""
listens for 100 active connections. This number can be
increased as per convenience.
"""
server.listen(100)

list_of_clients = []  # armazena a lista de clientes
list_of_nicknames = []  # armazena a lista de apelidos dos clientes
list_of_rooms = [
    {"name": "FGA",
     "connections": [],
     "members": [],
     "capacity": 30},
    {"name": "PATIO",
     "connections": [],
     "members": [],
     "capacity": 30},
    {"name": "RU",
     "connections": [],
     "members": [],
     "capacity": 20},
    {"name": "BCE",
     "connections": [],
     "members": [],
     "capacity": 0},
]

"""Metodo que ira tratar conexoes com os clientes
sempre buscando receber uma mensagem e fazendo o broadcast
para os demais clientes"""


def handle(conn):
    while True:
        # try:
        msg = message = conn.recv(2048)
        if msg.decode('ascii').startswith('KICK'):
            if list_of_nicknames[list_of_clients.index(conn)] == 'admin':
                name_to_kick = msg.decode('ascii')[5:]
                kick_user(name_to_kick)
            else:
                conn.send('Comando foi recusado!'.encode('ascii'))
        elif msg.decode('ascii').startswith('BAN'):
            if list_of_nicknames[list_of_clients.index(conn)] == 'admin':
                name_to_ban = msg.decode('ascii')[4:]
                kick_user(name_to_ban)
                with open('bans.txt', 'a') as f:
                    f.write(f'{name_to_ban}\n')
                print(f'{name_to_ban} foi banido!')
            else:
                conn.send('Comando foi recusado!'.encode('ascii'))
        elif msg.decode('ascii').startswith('QUIT'):
            conn.send('QUIT'.encode('ascii'))
            remove(conn)
            return
        else:
            broadcast(message)
            # except:
        # print('aiaiai')
        # remove(conn)
        # break


"""Using the below function, we broadcast the message to all
clients who's object is not the same as the one sending
the message"""


def broadcast(message):
    for client in list_of_clients:
        client.send(message)


"""The following function simply removes the object
from the list that was created at the beginning of
the program"""


def remove(connection):
    index = list_of_clients.index(connection)
    list_of_clients.remove(connection)
    print(connection.getpeername(), "disconnected")
    connection.close()
    nickname = list_of_nicknames[index]
    list_of_nicknames.remove(nickname)
    broadcast(f'{nickname} saiu do chat'.encode('ascii'))


def receive():
    while True:

        """Accepts a connection request and stores two parameters,
        conn which is a socket object for that user, and addr
        which contains the IP address of the client that just
        connected"""
        conn, addr = server.accept()

        # # prints the address of the user that just connected
        print(f"{str(addr)} connected")

        conn.send(get_rooms(list_of_rooms).encode('ascii'))
        room = conn.recv(2048).decode('ascii')

        # Envia uma palavra chave para o cliente escolher apelido
        conn.send('NICK'.encode('ascii'))
        nickname = conn.recv(2048).decode('ascii')

        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if nickname+'\n' in bans:
            conn.send('BAN'.encode('ascii'))
            conn.close()
            continue

        if nickname == 'admin':
            conn.send('PASS'.encode('ascii'))
            password = conn.recv(2048).decode('ascii')

            if password != 'admin':
                conn.send('RECUSADO'.encode('ascii'))
                conn.close()
                continue

        """Maintains a list of clients and nicknames for ease of broadcasting
		a message to all available people in the chatroom"""
        list_of_clients.append(conn)
        list_of_nicknames.append(nickname)

        # Mostra no server o apelido do cliente
        print(f'apelido do cliente e {nickname}')
        # faz um broadcast a todos sobre o cliente
        broadcast(f'{nickname} entrou no chat'.encode('ascii'))

        # sends a message to the client whose user object is conn
        conn.send(f'\nBem vindo ao chat {nickname}!'.encode('ascii'))

        # cria uma thread que ira tratar o cliente
        thread = threading.Thread(target=handle, args=(conn,))
        thread.start()  # inicia a thread


def kick_user(name):
    if name in list_of_nicknames:
        name_index = list_of_nicknames.index(name)
        client_to_kick = list_of_clients[name_index]
        list_of_clients.remove(client_to_kick)
        client_to_kick.send(
            'Voce foi expulso da sala de bate papo'.encode('ascii'))
        client_to_kick.close()
        list_of_nicknames.remove(name)
        broadcast(f'{name} foi expulso pelo admin'.encode('ascii'))


print('Escutando servidor')
receive()
