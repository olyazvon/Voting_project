#THE MAIN VOTING SCRIPT

import cx_Oracle
from hashlib import scrypt
from time import sleep
from os import name as os_name, system as os_system

#Globals

username = 'election_admin'
password = '1234'
with open('salt.txt', 'r') as saltFile:
	salt = saltFile.read()

#Functions

def voterCheckQuery(hashkey, connection):
	cursor = connection.cursor()
	#TODO: implement
	return True, 'You can vote here'
	#return False, 'This is not your tally center'
	#return False, 'You have voted already'
	#...

def voteQuery(hashkey, vote, connection):
	cursor = connection.cursor()
	pass
	#TODO: implement

def checkVoteInDbQuery(hashkey, vote, connection):
	cursor = connection.cursor()
	#TODO: implement
	return True

def paillier(data):
	#TODO: implement
	return 'encripted string'

def clearConsole():
	# For Windows
	if os_name == 'nt':
		os_system('cls')
	# For Unix
	else:
		os_system('clear')

#Main flow

centerNumber = input("Enter the tally center number: ")

#Database connection
with cx_Oracle.connect(user=username, password=password, 
	dsn='localhost/xe') as connection:


	#Main loop
	while True:
		clearConsole()
		print(f"Hello! Welcome to tally center No. {centerNumber}")
		#Ask for name, surname, ID
		voterName = input("Введите имя пользователя: ").encode()
		voterSurname = input("Введите фамилию пользователя: ").encode()
		voterID = input("Введите id пользователя ").encode()
		#Hash them
		hashkey = scrypt(voterName+voterSurname+voterID, 
			salt=salt.encode(), n=16384, r=8, p=1)

		#SQL request
		canVote, reason = voterCheckQuery(hashkey)

		#Print response, try again
		print(reason)
		if not canVote:
			print('You can try again in 5 seconds...')
			sleep(5)
			continue

		#Vote cycle
		vote = input("You are voting now! Type D or R and press Enter: ")
		while vote not in ('D','R'):
			vote = input('Wrong character, try again. Type D or R and press Enter: ')

		#Encrypt with paillier
		encryptedVote = paillier(vote)

		#SQL request
		voteQuery(hashkey, encryptedVote)

		#Check is the vote saved correctly
		print("Success! Have a nice day!" 
			if checkVoteInDbQuery(hashkey, encryptedVote) 
			else "Something went wrong. Please try again.")

		print("The screen will clear in 5 seconds")
		sleep(5)

