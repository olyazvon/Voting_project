# THE MAIN VOTING SCRIPT

import cx_Oracle
from hashlib import scrypt
from time import sleep
from os import name as os_name, system as os_system
from phe import paillier

# Globals

username = 'election_admin'
password = '1234'
with open('salt.txt', 'r') as saltFile:
	salt = saltFile.read()
with open('paillier_public_key.txt', 'r') as keyFile:
	n = int(keyFile.read())
	paillier_public_key = paillier.PaillierPublicKey(n)
MAX_VOTERS = 100000000


# Functions

def getID(phrase):
	voterID = input(phrase)
	while (not voterID.isdigit) or len(voterID) != 9:
		voterID = input("This field must consist of 9 digits. Try again: ")
	return(voterID)

def getName(phrase):
	voterName = input(phrase)
	tmp = voterName.replace(' ', '').replace('-', '')
	while (not tmp.isalpha()) or len(tmp) == 0:
		voterName = input("This field may contain only letters, space and dash. Try again: ")
		tmp = voterName.replace(' ', '').replace('-', '')
	return(voterName)

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
	checkResult = cursor.execute(
		'''SELECT * FROM Voters
		WHERE hashKey = :hash AND vote = :vote''',
		hash=hashkey, vote=vote.ljust(154)).fetchone()
	return False if checkResult == None else True

def paillier_encrypt(data):
	result = paillier_public_key.raw_encrypt(data)
	return str(result)

def clearConsole():
	# cls for Windows, clear for Unix
	os_system('cls' if os_name == 'nt' else 'clear')


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
		voterName = getName("Enter voter's name: ").encode()
		voterSurname = getName("Enter voter's surname: ").encode()
		voterID = getID("Enter voter's ID: ").encode()
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

		if vote == 'D':
			vote = MAX_VOTERS
		if vote == 'R':
			vote = 1

		# Encrypt with paillier
		encryptedVote = paillier_encrypt(vote)

		# SQL request
		voteQuery(hashkey, encryptedVote, connection)

		# Check is the vote saved correctly
		print("Success! Have a nice day!" 
			if checkVoteInDbQuery(hashkey, encryptedVote, connection)
			else "Something went wrong, your vote is not saved. Please try again.")

		print("The screen will clear in 5 seconds")
		sleep(5)

