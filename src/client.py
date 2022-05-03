# Python program to implement client side of chat room.
from ast import While
import socket
import select
import sys
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# if len(sys.argv) != 3:
# 	print ("Correct usage: script, IP address, port number")
# 	exit()

IP_address = '127.0.0.1'
Port = 8080
server.connect((IP_address, Port))


nickname = input("escolha um apelido: ")
if nickname == 'admin':
  password = input('Digite a senha para o admin: ')

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
      if message ==  'NICK':
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
      else:
        print(message)
    except:
      print("Ocorreu um erro")
      server.close()
      break

"""funcao que ira escrever mandar a mensagem e nick do cliente
para o servidor, onde sera feito o broadcast para os demais clientes"""
def write():
  while True:
    if stop_thread == True:
      break
    message = f'<{nickname}> {input("")}'
    if message[len(nickname)+3:].startswith('/'):
      if nickname == 'admin':
        if message[len(nickname)+3:].startswith('/kick'):
          server.send(f'KICK {message[len(nickname)+3+6:]}'.encode('ascii'))
        if message[len(nickname)+3:].startswith('/ban'):
          server.send(f'BAN {message[len(nickname)+3+5:]}'.encode('ascii'))

      else:
        print("Comandos reservados apenas para admin")
    else:
      server.send(message.encode('ascii'))

"""Definicao das threads que vão o tempo todo receber e escrever
para o server"""
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
