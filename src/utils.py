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
    return room
        