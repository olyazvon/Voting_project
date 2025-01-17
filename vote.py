# THE MAIN VOTING SCRIPT
# When using pyCharm, run in the terminal!

import getpass
import cx_Oracle
from hashlib import scrypt
from time import sleep
from os import name as os_name, system as os_system
from phe import paillier
from random import SystemRandom

# Constants

MAX_VOTERS = 10000
SALT_FILE = 'salt.txt'
PAILLIER_PUB_KEY_FILE = 'paillier_public_key.txt'

# Functions

def readFile(filename):
	# Read a file (exit in case of error)
	try:
		with open(filename, encoding='utf-8') as file:
				contents = file.read()
		return contents
	except FileNotFoundError:
			print(f"File {filename} doesn't exist")
			exit(1)

def getID(phrase):
	# Get a valid ID from keyboard
	voterID = input(phrase)
	while (not voterID.isdigit) or len(voterID) != 9:
		voterID = input("This field must consist of 9 digits. Try again: ")
	return(voterID)

def getName(phrase):
	# Get a valid name or surname from keyboard
	voterName = input(phrase)
	tmp = voterName.replace(' ', '').replace('-', '')
	while (not tmp.isalpha()) or len(tmp) == 0:
		voterName = input("This field may contain only letters, space and dash. Try again: ")
		tmp = voterName.replace(' ', '').replace('-', '')
	return(voterName)

def voterCheckQuery(hashkey, thisCenter, connection):
	# Check if the voter can vote, return a tuple of bool and str reason
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
	# Send a vote to DB
	cursor = connection.cursor()
	cursor.execute(
		'''UPDATE Voters
		SET vote = :vote
		WHERE hashKey = :hash''',
		vote=vote, hash=hashkey)
	connection.commit()


def checkVoteInDbQuery(hashkey, vote, connection):
	# Check if the vote in DB
	cursor = connection.cursor()
	checkResult = cursor.execute(
		'''SELECT * FROM Voters
		WHERE hashKey = :hash AND vote = :vote''',
		hash=hashkey, vote=vote.ljust(10)).fetchone()
	return False if checkResult == None else True

def paillier_encrypt(data):
	# Encrypt data with paillier encryption
	obf = SystemRandom().randrange(1, 150)
	result = paillier_public_key.raw_encrypt(data, r_value=obf)
	return str(result)

def clearConsole():
	# cls for Windows, clear for Unix
	os_system('cls' if os_name == 'nt' else 'clear')

def main():
	# Logging in and the main cycle
	username = input("Input admin username: ")
	password = getpass.getpass(prompt="Input admin password: ")

	with cx_Oracle.connect(user=username, password=password,
		dsn='localhost/xe') as connection:
		print("You are logged in!")
		centerNumber = int(input("Enter the tally center number: "))
		# Reception loop
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

			# Check if the voter can vote
			canVote, reason = voterCheckQuery(hashkey, centerNumber, connection)
			# Print response, try again in case of fail
			print(reason)
			if not canVote:
				print('You can try again in 5 seconds...')
				sleep(5)
				continue

			# Voting loop
			vote = input("You are voting now! Type D or R and press Enter: ")
			while vote not in ('D','R'):
				vote = input('Wrong character, try again. Type D or R and press Enter: ')
			# Convert the vote to a numeric value
			if vote == 'D':
				vote = MAX_VOTERS
			if vote == 'R':
				vote = 1

			# Encrypt the vote with paillier
			encryptedVote = paillier_encrypt(vote)
			# Send the vote to DB
			voteQuery(hashkey, encryptedVote, connection)

			# Check is the vote saved correctly
			print("Success! Have a nice day!"
				if checkVoteInDbQuery(hashkey, encryptedVote, connection)
				else "Something went wrong, your vote is not saved. Please try again.")

			print("The screen will clear in 5 seconds")
			sleep(5)


# Main flow

# Read the crucial files, get salt and paillier public key
salt = readFile(SALT_FILE)
n = int(readFile(PAILLIER_PUB_KEY_FILE))
paillier_public_key = paillier.PaillierPublicKey(n)


# Run main repatedly, if log in failed
while True:
	try:
		main()
	except cx_Oracle.DatabaseError as exc:
		error_code = exc.args[0].code
		if error_code == 1017:
			print("Invalid username or password.")
		elif error_code == 1005:
			print("No password provided")
		elif error_code == 28000:
			print("User is locked.")
		else:
			print("Database error:", exc)
	except KeyboardInterrupt:
		print("\nVoting stopped.")
		break