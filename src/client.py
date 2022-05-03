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

"""Função que receberar as mensagens. Aqui tambem ocorre a
identificação do recebimento da plavra chave NICK que permite
o envio do apelido para o servidor. Se ocorrer algum erro é
fechado a conexao"""
def receive():
  while True:
    try: 
      message = server.recv(2048).decode('ascii')
      if message ==  'NICK':
        server.send(nickname.encode('ascii'))
      else:
        print(message)
    except:
      print("ocorreu um erro")
      server.close()
      break

"""funcao que ira escrever mandar a mensagem e nick do cliente
para o servidor, onde sera feito o broadcast para os demais clientes"""
def write():
  while True:
    message = f'<{nickname}> {input("")}'
    server.send(message.encode('ascii'))

"""Definicao das threads que vão o tempo todo receber e escrever
para o server"""
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
