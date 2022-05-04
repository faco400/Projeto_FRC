# Python program to implement client side of chat room.
from ast import While
import socket
import select
import sys
import threading
from utils import choice_room

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# if len(sys.argv) != 3:
# 	print ("Correct usage: script, IP address, port number")
# 	exit()

IP_address = '127.0.0.1'
Port = 8080
server.connect((IP_address, Port))

nickname = input("Digite seu apelido: ")
if nickname == 'admin':
    password = input('Digite a senha para o admin: ')

rooms = server.recv(2048).decode('ascii')
print(rooms)
room = choice_room(rooms)
server.send(str(room).encode('ascii'))

stop_thread = False

"""Função que receberar as mensagens. Aqui tambem ocorre a
identificação do recebimento da plavra chave NICK que permite
o envio do apelido para o servidor. Se ocorrer algum erro é
fechado a conexao"""


def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = server.recv(2048).decode('ascii')
            if message == 'NICK':
                server.send(nickname.encode('ascii'))
                next_message = server.recv(2048).decode('ascii')
                if next_message == 'PASS':
                    server.send(password.encode('ascii'))
                    if server.recv(2048).decode('ascii') == 'REFUSE':
                        print("Conexao foi recusada. Senha errada")
                        stop_thread = True
                elif next_message == 'BAN':
                    print("Conexao recusada por causa de ban")
                    server.close()
                    stop_thread = True
            if message == 'QUIT':
                print('Saindo...')
                stop_thread = True
            else:
                if not message == 'NICK':
                    print(message)
        except:
            print("Ocorreu um erro")
            server.close()
            break


"""funcao que ira escrever mandar a mensagem e nick do cliente
para o servidor, onde sera feito o broadcast para os demais clientes"""


def write():
    admin_commands = ['\\kick', '\\ban']
    while True:
        global stop_thread
        if stop_thread == True:
            break
        message = f'<{nickname}> {input("")}'
        if message[len(nickname)+3:].startswith('\\'):
            cmd = message[message.index('\\'):]
            command = ""
            for c in cmd:
                if c == ' ':
                    break
                command += c
            if nickname == 'admin':
                if command == '\\kick':
                    server.send(
                        f'KICK {message[len(nickname)+3+6:]}'.encode('ascii'))
                if command == '\\ban':
                    server.send(
                        f'BAN {message[len(nickname)+3+5:]}'.encode('ascii'))
            elif command in admin_commands:
                print("Comandos reservados apenas para admin")
            elif command == '\\quit':
                server.send(f'QUIT {nickname}'.encode('ascii'))
                stop_thread = True
            elif command == '\\l':
                server.send(f'LS {room}'.encode('ascii'))
            elif command == '\\help':
                print("\\quit - Sair do chat")
                print("\\l    - Listar os participantes da sala")
                print()
        else:
            server.send(message.encode('ascii'))


"""Definicao das threads que vão o tempo todo receber e escrever
para o server"""
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
