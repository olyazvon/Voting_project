# THE MAIN VOTING SCRIPT

import cx_Oracle
from hashlib import scrypt
from time import sleep
from os import name as os_name, system as os_system

# Globals

username = 'election_admin'
password = '1234'
with open('salt.txt', 'r') as saltFile:
	salt = saltFile.read()

# Functions

def voterCheckQuery(hashkey, thisCenter, connection):
	cursor = connection.cursor()
	checkResult = cursor.execute(
		'''SELECT tallyCenter, DECODE(vote, NULL, 0, 1) AS voted
		FROM Voters WHERE hashKey = :hash''',
		hash=hashkey).fetchone()
	if checkResult == None:
		return False, 'Voter not found. Check your personal data.'
	assignedCenter, voted = checkResult
	if voted:
		return False, 'You have already voted.'
	if assignedCenter != thisCenter:
		return False, f'This is not your tally center. Go to the center No. {assignedCenter}'
	return True, 'You can vote here and now'

def voteQuery(hashkey, vote, connection):
	cursor = connection.cursor()
	cursor.execute(
		'''UPDATE Voters
		SET vote = :vote
		WHERE hashKey = :hash''',
		vote=vote, hash=hashkey)
	connection.commit()


def checkVoteInDbQuery(hashkey, vote, connection):
	cursor = connection.cursor()
	# TODO: implement
	return True

def paillier(data):
	# TODO: implement
	return data

def clearConsole():
	# For Windows
	if os_name == 'nt':
		os_system('cls')
	# For Unix
	else:
		os_system('clear')

# Main flow

centerNumber = int(input("Enter the tally center number: "))

# Database connection
with cx_Oracle.connect(user=username, password=password, 
	dsn='localhost/xe') as connection:

	# Main loop
	while True:
		clearConsole()
		print(f"Hello! Welcome to tally center No. {centerNumber}")
		# Ask for name, surname, ID
		voterName = input("Enter voter's name: ").encode()
		voterSurname = input("Enter voter's surname: ").encode()
		voterID = input("Enter voter's ID: ").encode()
		# Hash them
		hashkey = scrypt(voterName+voterSurname+voterID, 
			salt=salt.encode(), n=16384, r=8, p=1)

		# SQL request
		canVote, reason = voterCheckQuery(hashkey, centerNumber, connection)

		# Print response, try again
		print(reason)
		if not canVote:
			print('You can try again in 5 seconds...')
			sleep(5)
			continue

		# Vote cycle
		vote = input("You are voting now! Type D or R and press Enter: ")
		while vote not in ('D','R'):
			vote = input('Wrong character, try again. Type D or R and press Enter: ')

		if vote == 'R':
			vote = '0000000100000000'
		if vote == 'D':
			vote = '0000000000000001'
		# Encrypt with paillier
		encryptedVote = paillier(vote)

		# SQL request
		voteQuery(hashkey, encryptedVote, connection)

		# Check is the vote saved correctly
		print("Success! Have a nice day!" 
			if checkVoteInDbQuery(hashkey, encryptedVote, connection)
			else "Something went wrong. Please try again.")

		print("The screen will clear in 5 seconds")
		sleep(5)

