import socket
import threading
from time import sleep
import json

count = 0

clients = {}
client_data = {}

# client_data = {"nicname": [0, 0, 0], "nicnmame2": [1, 1, 1]}


def clientInfoRecv(client, client_ip):
	global clients
	global client_data

	while True:
		try: data = client.recv(1024).decode().replace('\'', '"')
		except ConnectionResetError as error:
			print(f'[{client_ip}] Problem with a host: \n{error}')
			return 0

		if data:  # data = {...}
			try:
				data = json.loads(data)

				if "eat" in data.keys():
					print(f'Message from client: {data}')

					deathKey = data['eat'] # dk = has been eaten
					print(f'Client {deathKey} has been eaten.')

					eatenCl = clients[deathKey]
					eatenCl.close()
					del clients[deathKey]
					del client_data[deathKey]

				else:
					pos = data["pos"]
					size = data["size"]

					newData = [pos, size]

					client_data[client_ip] = newData
			except Exception as error: 
				print(f'Error with client {client_ip}\n{error}')

def clientInfoSend(client, client_ip):
	client.send(client_ip.encode())
	while True:
		try:
			sleep(0.02)
			dataForSend = str(client_data).encode()
			client.send(dataForSend) # client.sendto(client_ip, text.encode())
		except: pass

def main():
	server = socket.socket()
	server.bind(('127.0.0.1', 4943))
	server.listen(5)

	while True:
		client, client_ip = server.accept()
		print('Connected ', client_ip)

		# clients['127.0.0.1:843']
		client_ip = f'{client_ip[0]}:{client_ip[1]}'
		clients[client_ip] = client # 1 port = 1 connection; 1 - 10000 port - services; 10001 - 65535 - connections
		client_data[client_ip] = [[0, 0], 10]

		threading.Thread(target=clientInfoRecv, args=(client, client_ip,), daemon=True).start()
		threading.Thread(target=clientInfoSend, args=(client, client_ip,), daemon=True).start()
		sleep(1)

if __name__ == '__main__': main()