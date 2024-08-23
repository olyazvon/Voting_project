# THE MAIN MANAGEMENT SCRIPT

import cx_Oracle
import sys
#from hashlib import scrypt
from phe import paillier

# Globals

MAX_VOTERS = 100000000
# TODO  удалить перед сдачей:
# username = 'election_admin'
# password = '1234'

username= input("input username")
password= input("input password")
# TODO:сделать из 3 функций  ниже 1 фунцию с обработкой исключений

def readFile(filename):
	try:
		with open(filename, encoding='utf-8') as file:
				contents = file.read()
		return contents
	except FileNotFoundError:
			print(f"File {filename} doesnt exist")
			sys.exit(1)

#salt=readFile('salt.txt')
n=int(readFile('paillier_public_key.txt'))
lines=readFile('paillier_private_key.txt').split("\n")
p = int(lines[0])
q = int(lines[1])


public_key = paillier.PaillierPublicKey(n)
private_key = paillier.PaillierPrivateKey(public_key, p, q)

# Functions

def showStatistics():
	cursor = connection.cursor()

	cursor.execute('''SELECT COUNT(*), COUNT(vote) FROM Voters''')
	allVoters, votedVoters = cursor.fetchone()

	cursor.execute('''SELECT vote FROM Voters WHERE vote IS NOT NULL''')
	votes = [paillier.EncryptedNumber(public_key, int(i[-1])) for i in cursor]
	if votes==[]:
		print("Nobody voted yet")
	else:
		totalSum = private_key.decrypt(sum(votes))
		dVotes, rVotes = divmod(totalSum, MAX_VOTERS)

		#print(f'Current results in the center No. {center}:')
		print(f'Voted: {votedVoters}/{allVoters} ({votedVoters/allVoters*100:.2f}%)')
		print(f'Respublicans: {rVotes/votedVoters*100:.2f}%, Democrats: {dVotes/votedVoters*100:.2f}%')




try:
	with cx_Oracle.connect(user=username, password=password,
	dsn='localhost/xe') as connection:
		print('Connection success')
		print('Welcome to admin utility for voting!')
		action = ''
		while action != '3':
			action = input('Enter 2 for current statistics, 3 for exit: ')
			if action == '2':
				showStatistics()
except cx_Oracle.DatabaseError:
	print("Failed to connect to DB, check login and password")

