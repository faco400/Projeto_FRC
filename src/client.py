import socket, os, threading, rsa
from utils import choice_room

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP_address = '127.0.0.1' # IP do servidor que se deseja conectar
Port = 8080 # Porta do servidor que se deseja conectar
server.connect((IP_address, Port)) # Realiza a conexão

"""Inputs iniciais do cliente. Caso seja admin pede-se a senha"""
nickname = input("Digite seu apelido: ")
if nickname == 'admin':
    password = input('Digite a senha para o admin: ')

rooms = server.recv(2048).decode('ascii') # cliente inicialmente recebe salas disponiveis do servidor
print(rooms) # imprime as salas do servidor no console
room = choice_room(rooms) # cliente escolhe sala para ingressar
server.send(str(room).encode('ascii')) # sala de escolha e enviada para o servidor

PRIVATE_KEY = ""

stop_thread = False # Variavel auxiliar para gerenciar o controle das threads

"""Função que receber e responder o servidor
de acordo com as palavras chaves
NICK (para envio do nickname)
PASS (para envio da senha de admin)
BAN(para desconectar cliente em caso de banimento)
QUIT (Para fechar conexao caso cliente deseje sair do chat)
ENCRYP (Para informar que recebeu uma mensagem encriptografada)
. Caso nao seja recebido nenhuma palavra chave entao se trata 
de uma mensagem para a leitura do cliente que sera impressa no console.
Se ocorrer algum erro também é fechado a conexao"""
def receive():
    while True:
        global stop_thread
        global PRIVATE_KEY
        if stop_thread:
            break
        try:
            message = server.recv(2048)
            if message[:4].decode('ascii') == 'NICK':
                message = message.decode('ascii')
                server.send(nickname.encode('ascii'))
                next_message = server.recv(2048)
                if next_message[:4].decode('ascii') == 'PASS':
                    server.send(password.encode('ascii'))
                    nnext_message = server.recv(2048)
                    if nnext_message[:6].decode('ascii') == 'REFUSE':
                        print("Conexao foi recusada. Senha errada")
                        stop_thread = True
                    if nnext_message[:6].decode('ascii') == "PRIKEY":

                        PRIVATE_KEY = rsa.key.PrivateKey.load_pkcs1(
                            nnext_message[6:], format='DER')

                elif next_message[:3].decode('ascii') == 'BAN':
                    print("Conexao recusada por causa de ban")
                    server.close()
                    stop_thread = True
                    os._exit(1)
                if next_message[:6].decode('ascii') == "PRIKEY":
                    PRIVATE_KEY = rsa.key.PrivateKey.load_pkcs1(
                        next_message[6:], format='DER')
                continue
            if message[:4].decode('ascii') == 'QUIT':
                print('Saindo...')
                stop_thread = True
                continue
            if message[:4].decode('ascii') == 'KICK':
                print('Voce foi expulso pelo admin')
                os._exit(1)
            if message[:6].decode('ascii') == "PRIKEY":
                PRIVATE_KEY = rsa.key.PrivateKey.load_pkcs1(
                    message[6:], format='DER')
                continue
            if message[:6].decode('ascii') == "ENCRYP":
                print("Mensagem criptografada recebida:")
                print(rsa.decrypt(message[6:], PRIVATE_KEY).decode('ascii'))
                continue
            print(message.decode('ascii'))
        except Exception as e:
            print("Ocorreu um erro", str(e))
            server.close()
            os._exit(1)


"""Funcao responsavel pela escrita e envio de mensagens que o cliente digitar no chat.
Em caso de mensagens comuns de dialogo no chat, o servidor ira recebe-las para realizar o broadcast
para os membros da sala de bate papo. Em caso de comandos especiais o servidor ira tratar esses comandos
de acordo com suas funcionalidades"""
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
            if command == '\\quit':
                server.send(f'QUIT {nickname}'.encode('ascii'))
                stop_thread = True
            if command == '\\l':
                server.send(f'LS {room}'.encode('ascii'))
            if command == '\\to': 
                server.send(f'TO {message[len(nickname)+3+4:]}'.encode('ascii'))
            if command == '\\help':
                print("\\quit        Sair do chat")
                print("\\l           Listar os participantes da sala")
                print("\\to <member> mensagem encriptografada para um membro")
                print()
        else:
            server.send(message.encode('ascii'))


"""Definicao das threads que vão o tempo todo receber e escrever
para o server"""
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
