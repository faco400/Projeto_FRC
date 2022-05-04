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
     "capacity": 20},
    {"name": "LAMA",
     "connections": [],
     "members": [],
     "capacity": 0},
]

"""Metodo que ira tratar conexoes com os clientes
sempre buscando receber uma mensagem e fazendo o broadcast
para os demais clientes"""


def handle(conn, room):
	try:
		while True:
			msg = conn.recv(2048).decode('ascii')
			if msg.startswith('KICK'):
				if room['members'][room['connections'].index(conn)] == 'admin':
					name_to_kick = msg[5:]
					kick_user(name_to_kick, "foi expulso pelo admin")
				else:
					conn.send('Comando foi recusado!'.encode('ascii'))
			elif msg.startswith('BAN'):
				if room['members'][room['connections'].index(conn)] == 'admin':
					name_to_ban = msg[4:]
					kick_user(name_to_ban, "foi banido pelo admin")
					with open('bans.txt', 'a') as f:
						f.write(f'{name_to_ban}\n')
				else:
					conn.send('Comando foi recusado!'.encode('ascii'))
			elif msg.startswith('LS '):
				r = int(msg.split(' ')[1])
				memb = "\n".join(list_of_rooms[r]['members'])
				conn.send(memb.encode('ascii'))
			elif msg.startswith('QUIT'):
				conn.send('QUIT'.encode('ascii'))
				remove(conn)
				return
			else:
				broadcast_room(msg, room)
	except:
		return


"""Using the below function, we broadcast the message to all
clients who's object is not the same as the one sending
the message"""


def broadcast(message):
    for client in [i for j in [r['connections'] for r in list_of_rooms] for i in j]:
        client.send(str(message).encode('ascii'))


def broadcast_room(message, room):
    for client in room['connections']:
        client.send(str(message).encode('ascii'))


"""The following function simply removes the object
from the list that was created at the beginning of
the program"""


def remove(connection, message="saiu da sala"):
    for room in list_of_rooms:
        if connection in room['connections']:
            i = room['connections'].index(connection)
            nickname = room['members'][i]
            room['members'].remove(nickname)
            room['connections'].remove(connection)
            room['capacity'] += 1
            print(connection.getpeername(), "disconnected")
            connection.close()
            broadcast_room(f'{nickname} {message}', room)
            return


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
        room = list_of_rooms[int(conn.recv(2048).decode('ascii'))]

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
        room['connections'].append(conn)
        room['members'].append(nickname)
        room['capacity'] -= 1

        # Mostra no server o apelido do cliente
        print(f'apelido do cliente eh {nickname}')
        # faz um broadcast a todos sobre o cliente
        broadcast_room(f'{nickname} entrou na sala', room)

        # sends a message to the client whose user object is conn
        room_name = room['name']
        hellcome_message = f'\nBem vindo a sala {room_name}, {nickname}!\n'
        hellcome_message += 'Para saber os comandos digite \\help\n'
        conn.send(hellcome_message.encode('ascii'))

        # cria uma thread que ira tratar o cliente
        thread = threading.Thread(target=handle, args=(conn, room))
        thread.start()  # inicia a thread


def kick_user(name, message):
    for room in list_of_rooms:
        if name in room['members']:
            i = room['members'].index(name)
            client_to_kick = room['connections'][i]
            client_to_kick.send('KICK'.encode('ascii'))
            remove(client_to_kick, message=message)
            return


print('Escutando servidor')
receive()
