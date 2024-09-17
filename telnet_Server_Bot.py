import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
server.bind(('localhost', 10000))
server.listen(5)

connections = []

print("Server Bot - Iniciado..")
print("Esperando respuesta de los clientes...\n")
while True:
    try:
        connection, address = server.accept()
        connection.setblocking(False)
        connections.append(connection)
    except BlockingIOError:
        pass

    for connection in connections:
        try:
            message = connection.recv(4096)
            if len(message) > 3: 
                print(f'{message}')
                if "sell" in message.decode('utf-8'): print("\n")
        except BlockingIOError:
            continue