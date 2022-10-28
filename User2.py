from socket import*
import threading
import sys
import time
import os
#import getch

socket2 = socket(AF_INET,SOCK_DGRAM)
socket2.bind(('',12001))

peer1Name = input("Hello! Please enter the name of this contact:")

ACK0 = 0
ACK1 = 0
sequenceNumber = 0
expectedSequenceNumber = 0
messageQueue = []
sep = "<SEPARATOR>"

def send():

	while True:
		sendMessage = input("")
		if(sendMessage == "I want to send file"):
			sendFile()
			sendMessage=''
		if "Bye" in sendMessage:
			sys.exit()
		messageQueue.append(sendMessage)

def sendC():

	global sequenceNumber
	global expectedSequenceNumber
	global ACK0
	global ACK1

	while True:	
		if (len(messageQueue) != 0):
			messageToSend = str(sequenceNumber) +  messageQueue.pop(0)
			socket2.sendto(messageToSend.encode(), ('127.0.0.1',12000))
			x1 = time.time()				
					
			while True:
				if (ACK0 == 1 and sequenceNumber == 0):
					sequenceNumber = 1 - sequenceNumber
					ACK0 = 1 - ACK0
					break

				elif (ACK1 == 1 and sequenceNumber == 1):
					sequenceNumber = 1 - sequenceNumber
					ACK1 = 1 - ACK1
					break

				if(time.time()-x1>0.4):
					messageQueue.insert(0,messageToSend[1:])
					break
                                                                            
def listen():

	global sequenceNumber
	global expectedSequenceNumber
	global ACK0
	global ACK1

	while True:

		receiveMessage=socket2.recvfrom(2048)
		message = receiveMessage[0].decode()
		
		if(message == "ACK0" and sequenceNumber == 0):
			ACK0 = 1
		elif(message == "ACK1" and sequenceNumber == 1):
			ACK1 = 1

		elif(message[0] == "0" and expectedSequenceNumber == 0):
			print("\t\t\t" + peer1Name + ":" + message[1:])
			expectedSequenceNumber = 1 - expectedSequenceNumber
			socket2.sendto("ACK0".encode(),('127.0.0.1',12000))
		  
		elif(message[0] == "1" and expectedSequenceNumber == 1):
			print("\t\t\t" + peer1Name + ":" + message[1:])
			expectedSequenceNumber = 1 - expectedSequenceNumber
			socket2.sendto("ACK1".encode(),('127.0.0.1',12000))

		if "Bye" in message:
			sys.exit()

def sendFile():

	fileName = input("What's the name of the file you want to send?\n")
	servername='127.0.0.1'
	serverport=12000
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((servername,serverport))
	clientSocket.send(f"{fileName}{sep}{2048}".encode())
	with open(fileName, "rb") as filedata:
		while True:
			data = filedata.read(4096)
			if not data:
				break
			clientSocket.sendall(data)
	clientSocket.close()
	print("The file was sent")

def receiveFile():

	serverSocket = socket(AF_INET,SOCK_STREAM)
	serverSocket.bind(('127.0.0.1',12001))
	serverSocket.listen(1)
	connectionSocket, addr = serverSocket.accept()
	recmsg = connectionSocket.recv(4096).decode()
	fileNameRec, size = recmsg.split(sep) 
	fileNameRec = os.path.basename(fileNameRec)
	
	with open(fileNameRec, "rb") as filedata, open(fileNameRec[:-4] + "Receiver" +fileNameRec[-4:], 'wb') as filedata2:
		while True:
			data2 = connectionSocket.recv(2048).decode()
			if not data2:
				break
			print("Data is being received")
			for line in filedata:
				filedata2.write(line)
	print("File was received")
	connectionSocket.close()
	serverSocket.close()

sendingThread = threading.Thread(target = send)
sendingCThread = threading.Thread(target = sendC)
listeningThread = threading.Thread(target = listen)
sendFileThread = threading.Thread(target = sendFile)
receiveFileThread = threading.Thread(target = receiveFile)
	
receiveFileThread.start()
listeningThread.start()
sendingThread.start()
sendingCThread.start()




