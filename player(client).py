import pygame
from pygame.locals import *
from random import *
from time import sleep
import socket
import threading
import math
import json


WINDOW_HEIGHT = 1000
WINDOW_WIDTH = 1000
FPS = 60
FOOD_NUM = 20
FOOD_SIZE = 15
client = None


pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

players_data = []
curPlayerRect = None
players_obj = {}
urIp = None
ifRunning = True

screen.fill('white')
pygame.display.flip()

def connect(plSqr):
	global client

	try:
		client = socket.socket()
		client.connect(('127.0.0.1', 4943))

		threading.Thread(target=playerInfoSend, args=(client, plSqr, ), daemon=True).start()
		threading.Thread(target=playersInfoRecv, args=(client, ), daemon=True).start()

		return client

	except ConnectionRefusedError:
		print("No server connection")
		sleep(1)

class Food:
	def __init__(self):
		self.poses = []
		self.valors = [10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 30]
		for i in range(FOOD_NUM):
			self.createFood	()
			

	def createFood(self):
		x = randint(0, 1000)
		y = randint(0, 1000)
		sc = choice(self.valors)
		self.poses.append([x, y, sc])


class Player:
	def __init__(self):

		self.cordX = randint(20, WINDOW_WIDTH - 20)
		self.cordY = randint(20, WINDOW_HEIGHT - 20)
		self.color = 'red'
		self.size = 100
		self.speed = 100 / self.size
		self.ballData = [self.cordX, self.cordY, self.size]


def collision(minXRange, minYRange, maxXRange, maxYRange, i):
	isCollide = False

	for j in range(minXRange, maxXRange):
		for k in range(minYRange, maxYRange):
			if j == i[0] and k == i[1]:
				isCollide = True
				break
		if isCollide:
			break

	return isCollide


def main():
	global ifRunning
	global players_data
	global players_obj
	global curPlayerRect

	plSqr = Player()
	plFood = Food()

	connect(plSqr)


	while ifRunning:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				ifRunning = False

		screen.fill('white')

		for i in range(FOOD_NUM):
			if plFood.poses[i][2] == 10:
				pygame.draw.rect(screen, pygame.Color(0, 0, 0), Rect(plFood.poses[i][0], plFood.poses[i][1], 5, 5))
			if plFood.poses[i][2] == 20:
				pygame.draw.rect(screen, pygame.Color(0, 0, 175), Rect(plFood.poses[i][0], plFood.poses[i][1], 5, 5))
			if plFood.poses[i][2] == 30:
				pygame.draw.rect(screen, pygame.Color(0, 0, 255), Rect(plFood.poses[i][0], plFood.poses[i][1], 5, 5))

		if len(players_data) > 0:
			for keyName in list(players_data.keys()):
				if keyName != urIp:
					plRect = Rect(players_data[keyName][0][0], players_data[keyName][0][1], math.sqrt(players_data[keyName][1]), math.sqrt(players_data[keyName][1]))
					players_obj[keyName] = plRect

					pygame.draw.rect(screen, 'green', plRect)

		curPlayerRect = Rect(plSqr.cordX, plSqr.cordY, math.sqrt(plSqr.size), math.sqrt(plSqr.size))

		pygame.draw.rect(screen, plSqr.color, curPlayerRect)

		keys = pygame.key.get_pressed()
		mUpdate(keys, plSqr, plFood)

		pygame.display.flip()

		clock.tick(FPS)

def mUpdate(keys, playeree, fodiee):
    if keys[pygame.K_w]:
    	if playeree.cordY > 0:
        	playeree.cordY -= playeree.speed
        	checkFood(playeree, fodiee)
    if keys[pygame.K_s]:
    	if playeree.cordY < 1000:
        	playeree.cordY += playeree.speed
        	checkFood(playeree, fodiee)
    if keys[pygame.K_a]:
    	if playeree.cordX > 0:
        	playeree.cordX -= playeree.speed
        	checkFood(playeree, fodiee)
    if keys[pygame.K_d]:
    	if playeree.cordX < 1000:
        	playeree.cordX += playeree.speed
        	checkFood(playeree, fodiee)
    playeree.ballData = [playeree.cordX, playeree.cordY, playeree.size]

def checkFood(playeree, fodiee):
	global players_data
	global client
	global players_obj
	global curPlayerRect
	global urIp

	minXRange = int(playeree.cordX - math.sqrt(playeree.size))
	maxXRange = int(playeree.cordX + math.sqrt(playeree.size))
	minYRange = int(playeree.cordY - math.sqrt(playeree.size))
	maxYRange = int(playeree.cordY + math.sqrt(playeree.size))
	
	for plKey, h in players_data.items():
		if plKey != urIp:
			plRect = players_obj[plKey]

			if pygame.Rect.colliderect(
					curPlayerRect, plRect
				):
					playeree.size += h[1]
					dataTS = '{"eat": "' + str(plKey) + '"}'
					client.send(dataTS.encode())
					sleep(0.01)
					break
				
				#break

	for i in fodiee.poses:
		collides = collision(minXRange, minYRange, maxXRange, maxYRange, i)
		if collides:
			playeree.size += i[2]
			fodiee.poses.remove(i)
			fodiee.createFood()

	isEaten = False




def playerInfoSend(client, plSqr):
	while True:
		#try:
			data = {"pos" : [plSqr.ballData[0], plSqr.ballData[1]], "size" : plSqr.ballData[2]}
			client.send(str(data).encode())
			sleep(0.01)
		# except:
		#	exit(0)

def playersInfoRecv(client):
	global players_data
	global urIp	

	urIp = client.recv(1024).decode()

	while True:
		try:
			players_data_raw = client.recv(1024).decode().replace('\'', '"')
			players_data = json.loads(players_data_raw)
		except: ...


if __name__ == '__main__':
	main()
	pygame.quit()