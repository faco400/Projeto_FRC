import rsa

def get_rooms(rooms_list: list) -> str:
    res = "Bem vindo ao trabalho final de FRC, aqui estao as nossas salas:\n"
    for i, room in enumerate(rooms_list):
        res += f"{i+1}) Sala: {room['name']}, Vagas: {room['capacity']}\n"
    return res

def choice_room(rooms: str) -> int:
    rooms = rooms.split('\n')[1:-1]
    success = False
    while not success:
        room = int(input("Escolha a sala: "))
        if not room in range(1, len(rooms)+1):
            print("Sala invalida!")
            continue
        capacity = int(rooms[room-1].rpartition(' ')[2])
        if capacity == 0:
            print("Sala lotada!")
            continue
        success = True
    return room - 1

def envia(msg, conn, room):
    print('olha o msg', msg)
    message = msg.split(' ')
    print('olha o strip', message)
    member_index = -1
    for i, member in enumerate(room['members']):
        if member == message[1]:
            member_index = i
            break
    if member_index == -1:
        print('not found member')
        print(message[1])
        return
    to_send = " ".join(message[2:])
    encMsg = rsa.encrypt(to_send.encode('ascii'), room['pub_keys'][member_index])
    pre = "ENCRYP"
    pre = pre.encode('ascii')
    room['connections'][member_index].send(pre + encMsg)
    