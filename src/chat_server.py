# Python program to implement server side of chat room.
from re import I
import socket
import threading, os
from utils import get_rooms


"""O primeiro argumento AF_INET e o endereco de dominio de socket.
Este e utilizado quando nos temos um dominio de internet com quaisquer dois hosts
O segundo argumento e o tupo de socket. SOCK_STREAM significa que o dado, ou
caracteres são lidos em um fluxo continuo"""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = "127.0.0.1"  # servidor vai rodar na maquina local
Port = 8080  # porta

"""Vincula o servidor a um IP em uma porta especifica.
O cliente deve ter conhecimento desses parametros"""
server.bind((host, Port))

"""Escuta por 100 conexoes ativas. Esse numero pode ser
aumentado de acordo com a necessidade."""
server.listen(100)

"""Este e a lista padrão de salas que iram estar disponiveis no inicio da aplicação"""
list_of_rooms = [
    {"name": "FGA",
     "connections": [],
     "members": [],
     "pub_keys": [],
     "capacity": 30},
    {"name": "RU",
     "connections": [],
     "members": [],
     "pub_keys": [],
     "capacity": 20}
]

"""Função que vai funcionar como um tratador de comandos para
o gerenciamento do servidor. Exibição de todas as salas existentes
Criação de salas/Exclusão de salas, o comando para desligar o servidor
e outro para fazer um broadcast a todos que estão conectados com o servidor"""
def manager():
    while True:
        cmd = input("").split(' ')
        if cmd[0] == "rooms":
            rooms = get_rooms(list_of_rooms)
            print(rooms[rooms.index('\n'):])
        elif cmd[0] == "create-room":
            if len(cmd) != 3:
                print(
                    "Sintaxe errada para o comando, o correto seria create-room <room-name> <capacity>")
                continue
            if not cmd[2].isdigit():
                print("Capacidede deve ser um digito")
                continue
            remain = 100 - sum([r['capacity'] for r in list_of_rooms])
            if int(cmd[2]) > remain:
                print(
                    "Nao eh possivel alocar uma sala desse tamanho, capacidade restante:", remain)
                continue
            list_of_rooms.append(
                {"name": cmd[1],
                 "connections": [],
                 "pub_keys": [],
                 "members": [],
                 "capacity": int(cmd[2])}
            )
            print("Sala", cmd[1], "criada com sucesso!")
        elif cmd[0] == "remove-room":
            if len(cmd) != 2:
                print("Sintaxe errada para o comando, o correto seria remove-room <room-name>")
                continue
            room_index = -1
            for i, r in enumerate(list_of_rooms):
                if r['name'] == cmd[1]:
                    room_index = i
                    break
            if room_index == -1:
                print("Nenhuma sala com esse nome")
                continue
            if list_of_rooms[room_index]['members']:
                print("Nao pode deletar uma sala com pessoas nela")
                continue
            del list_of_rooms[room_index]
            print("Sala deletada", cmd[1],"com sucesso!")
        elif cmd[0] == "broadcast":
            if len(cmd) < 1:
                print("Sintaxe errada, voce deve passar algo apos o comando")
            broadcast(" ".join(cmd[1:]))
        elif cmd[0] == "shutdown":
            os._exit(0)
        elif cmd[0] == "help":
            print()
            print("rooms                                 Listar todas as salas")
            print("create-room <room-name> <capacity>    Criar sala")
            print("remove-room <room-name>               Deletar sala")
            print("broadcast <arg1> ... <argN>           Mensagem para todos os participantes")
            print("shutdown                              Desligamento do servidor")
            print()
        else:
            print("Comando", cmd[0], "nao existe")

"""Esse metodo será o tratador de mensagens recebidas do lado cliente. 
Aqui se recebe palavras chaves em letras maíusculas que indicam o que
o cliente deseja que o servidor realize. KICK para expulsar alguem do chat. BAN
para banir alguem, LS para listar membros do chat, QUIT para fechar a conexao do user
com o servidor"""
def handle(conn, room):
    try:
        while True:
            # Recebe mensagem com palavra chave do cliente
            msg = conn.recv(2048).decode('ascii')

            if msg.startswith('KICK'): # Mensagem começa com paravra chave KICK server inicia a expulsao do cliente
                if room['members'][room['connections'].index(conn)] == 'admin':
                    name_to_kick = msg[5:]
                    kick_user(name_to_kick, "foi expulso pelo admin")
                else:
                    conn.send('Comando foi recusado!'.encode('ascii'))

            elif msg.startswith('BAN'): # Mensagem começa com paravra chave BAN server inicia o banimento do cliente
                if room['members'][room['connections'].index(conn)] == 'admin':
                    name_to_ban = msg[4:]
                    kick_user(name_to_ban, "foi banido pelo admin")
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                else:
                    conn.send('Comando foi recusado!'.encode('ascii'))

            elif msg.startswith('LS '): # Mensagem começa com paravra chave LS server inicia lista as salas para cliente
                r = int(msg.split(' ')[1])
                memb = "\n".join(list_of_rooms[r]['members'])
                conn.send(memb.encode('ascii'))

            elif msg.startswith('QUIT'): # Mensagem é palavra chave QUIT, servidor fecha a conexao com o cliente
                conn.send('QUIT'.encode('ascii'))
                remove(conn)
                return
            elif msg.startswith('TO '):
                envia(msg, conn, room)
            else:
                broadcast_room(msg, room)
    except:
        return


"""Usando a funçao abaixo, e feito o broadcast de mensagens para todos os clientes 
de todas as salas cujo objeto nao e o mesmo que esta enviando a mensagem"""
def broadcast(message):
    for client in [i for j in [r['connections'] for r in list_of_rooms] for i in j]:
        client.send(str(message).encode('ascii'))

"""Usando a funçao abaixo, e feito o broadcast de mensagens para todos os clientes 
de uma sala especifica cujo objeto nao e o mesmo que esta enviando a mensagem"""
def broadcast_room(message, room):
    for client in room['connections']:
        client.send(str(message).encode('ascii'))

""""A função a seguir tem como papel principal a remoção de um socket cliente conectado ao servidor
procurando remover o elemento da sala e atualizar a capacidade de determinada sala.
Utilizado para remover alguem do chat"""
def remove(connection, message="saiu da sala"):
    for room in list_of_rooms:
        if connection in room['connections']:
            i = room['connections'].index(connection)
            nickname = room['members'][i]
            pubkey = room['pub_keys'][i]
            room['members'].remove(nickname)
            room['connections'].remove(connection)
            room['pub_keys'].remove(pubkey)
            room['capacity'] += 1
            print(connection.getpeername(), "disconnected")
            connection.close()
            broadcast_room(f'{nickname} {message}', room)
            return

"""Funcao que ira enviar palavras chaves e receber suas respostas
do cliente a fim de fazer a manutençao das listas do chat(conexões, membros e capacidade).
Ela também auxilia na criação do apelido do usuario e eh essencial para criação de threads que iram tratar
os principais comandos do cliente."""
def receive():
    while True:
        """Aceita as requisiçoes de conexao e armazena dois parametros
        conn que e o socket objeto para aquele cliente, e o endereco que contem
        o IP do cliente que acabou de conectar"""
        conn, addr = server.accept()

        # Imprime no console que o cliente acabou de se conectar
        print(f"{str(addr)} connected")

        """Envia para o cliente a lista de salas disponiveis 
        e recebe do cliente a sala que deseja ingressar"""
        conn.send(get_rooms(list_of_rooms).encode('ascii'))
        room = list_of_rooms[int(conn.recv(2048).decode('ascii'))]

        # Envia uma palavra chave para o cliente escolher apelido
        conn.send('NICK'.encode('ascii'))
        nickname = conn.recv(2048).decode('ascii')

        #Abre o txt com os bans do chat
        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        # Verifica se nickname se encontra na lista de bans
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

        """Mantem a lista de clientes e apelidos assim como a capacidade da sala
        A fim de facilitar o broadcast de mensagem para os clientes disponiveis no chat"""
        publicKey, privateKey = rsa.newkeys(512)
        privateKey_str = privateKey.save_pkcs1(format='DER')
        pre = "PRIKEY".encode('ascii')
        conn.send(pre+privateKey_str)

        """Maintains a list of clients and nicknames for ease of broadcasting
		a message to all available people in the chatroom"""
        room['connections'].append(conn)
        room['members'].append(nickname)
        room['pub_keys'].append(publicKey)
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


"""Funcao auxiliar para a tirar o cliente do chat e desconecta-lo da aplicação."""
def kick_user(name, message):
    for room in list_of_rooms:
        if name in room['members']:
            i = room['members'].index(name)
            client_to_kick = room['connections'][i]
            client_to_kick.send('KICK'.encode('ascii'))
            remove(client_to_kick, message=message)
            return


print('Escutando servidor') #Aparece que o servidor esta escutando no console do chat_server
thread = threading.Thread(target=manager) # Criar a thread de genrenciamento do servidor
thread.start()  # inicia a thread
receive() # O servidor começa o seu dialogo com o cliente
