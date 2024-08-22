# THE MAIN MANAGEMENT SCRIPT

import cx_Oracle
#from hashlib import scrypt
from phe import paillier

# Globals

MAX_VOTERS = 100000000

username = 'election_admin'
password = '1234'
with open('salt.txt', 'r') as saltFile:
	salt = saltFile.read()

with open('paillier_public_key.txt') as f:
	n = int(f.read())

with open('paillier_private_key.txt') as f:
	p = int(f.readline())
	q = int(f.readline())

public_key = paillier.PaillierPublicKey(n)
private_key = paillier.PaillierPrivateKey(public_key, p, q)

# Functions

def showStatistics():
	cursor = connection.cursor()

	cursor.execute('''SELECT COUNT(*), COUNT(vote) FROM Voters''')
	allVoters, votedVoters = cursor.fetchone()

	cursor.execute('''SELECT vote FROM Voters WHERE vote IS NOT NULL''')
	votes = [paillier.EncryptedNumber(public_key, int(i[-1])) for i in cursor]
	
	totalSum = private_key.decrypt(sum(votes))

	dVotes, rVotes = divmod(totalSum, MAX_VOTERS)

	#print(f'Current results in the center No. {center}:')
	print(f'Voted: {votedVoters}/{allVoters} ({votedVoters/allVoters*100:.2f}%)')
	print(f'Respublicans: {rVotes/votedVoters*100:.2f}%, Democrats: {dVotes/votedVoters*100:.2f}%')


print('Welcome to admin utility for voting!')

with cx_Oracle.connect(user=username, password=password, 
	dsn='localhost/xe') as connection:
	print('Connection success')

	action = ''
	while action != '3':
		action = input('Enter 2 for current statistics, 3 for exit: ')
		if action == '2':
			showStatistics()
