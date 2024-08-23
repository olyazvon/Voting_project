# THE MAIN MANAGEMENT SCRIPT

import cx_Oracle
import sys
import os
#from hashlib import scrypt
from phe import paillier
from pysnark.qaptools.runqapver import run as verify
from subprocess import run, DEVNULL


# Globals

MAX_VOTERS = 10000
centers = (1, 2, 3)
# TODO  удалить перед сдачей:
username = 'election_admin'
password = '1234'

# username = input("Input username: ")
# password = input("Input password: ")
# TODO:сделать из 3 функций  ниже 1 фунцию с обработкой исключений

def readFile(filename):
	try:
		with open(filename, encoding='utf-8') as file:
				contents = file.read()
		return contents
	except FileNotFoundError:
			print(f"File {filename} doesn't exist")
			sys.exit(1)

n=int(readFile('paillier_public_key.txt'))
lines=readFile('paillier_private_key.txt').split("\n")
p = int(lines[0])
q = int(lines[1])


public_key = paillier.PaillierPublicKey(n)
private_key = paillier.PaillierPrivateKey(public_key, p, q)

# Functions

# def showStatistics():
# 	cursor = connection.cursor()

# 	cursor.execute('''SELECT COUNT(*), COUNT(vote) FROM Voters''')
# 	allVoters, votedVoters = cursor.fetchone()

# 	cursor.execute('''SELECT vote FROM Voters WHERE vote IS NOT NULL''')
# 	votes = [paillier.EncryptedNumber(public_key, int(i[-1])) for i in cursor]
# 	if votes==[]:
# 		print("Nobody voted yet")
# 	else:
# 		totalSum = private_key.decrypt(sum(votes))
# 		dVotes, rVotes = divmod(totalSum, MAX_VOTERS)

# 		#print(f'Current results in the center No. {center}:')
# 		print(f'Voted: {votedVoters}/{allVoters} ({votedVoters/allVoters*100:.2f}%)')
# 		print(f'Respublicans: {rVotes/votedVoters*100:.2f}%, Democrats: {dVotes/votedVoters*100:.2f}%')

def storeFiles(center):
	if os.path.exists('pysnark_values_' + str(center)):
		os.remove('pysnark_values_' + str(center))
	os.rename('pysnark_values', 'pysnark_values_' + str(center))
	if os.path.exists('pysnark_proof_' + str(center)):
		os.remove('pysnark_proof_' + str(center))
	os.rename('pysnark_proof', 'pysnark_proof_' + str(center))

def prepareFiles(center):
	if os.path.exists('pysnark_values'):
		os.remove('pysnark_values')
	os.rename('pysnark_values_' + str(center), 'pysnark_values')
	if os.path.exists('pysnark_proof'):
		os.remove('pysnark_proof')
	os.rename('pysnark_proof_' + str(center), 'pysnark_proof')

def loadData():
	with open('pysnark_values') as f:
		#dVotes = f.readlines()[-2].split(' ')[-1][:-1]
		#rVotes = f.readlines()[-1].split(' ')[-1][:-1]
		l = f.readlines()
		return [int(l[i].split(' ')[-1][:-1]) for i in (1, 2, -2, -1)]

def showData(data):
	allVoters, votedVoters, dVotes, rVotes = data
	print(f'    Voted: {votedVoters}/{allVoters} ({votedVoters/allVoters*100:.2f}%)')
	print(f'    Respublicans: {rVotes/votedVoters*100:.2f}%, Democrats: {dVotes/votedVoters*100:.2f}%')

def partialResult(center):
	cursor = connection.cursor()

	#two sql requests
	cursor.execute(
		'''SELECT COUNT(*), COUNT(vote) FROM Voters
		WHERE tallyCenter = :center''',
		center=center)
	allVoters, votedVoters = cursor.fetchone()

	cursor.execute(
		'''SELECT vote FROM Voters
		WHERE vote IS NOT NULL AND tallyCenter = :center''',
		center=center)
	votes = [paillier.EncryptedNumber(public_key, int(i[-1])) for i in cursor]
	votes.append(public_key.encrypt(0))

	print(f'In the center No. {center}:')

	#sum votes
	encryptedSum = sum(votes).ciphertext()

	#zkp decrypt
	run(['python', 'decrypt.py', str(encryptedSum), str(allVoters), str(votedVoters)], 
		stdout=DEVNULL, stderr=DEVNULL)

	if votedVoters == 0:
		print("    Nobody has voted yet.")
	else:
	#load data
	#show data
		showData(loadData())

	#file rename
	storeFiles(center)

	#del extra files
	os.remove('pysnark_eqs')
	os.remove('pysnark_wires')
	if os.path.exists('pysnark_mastersk'):
		os.remove('pysnark_mastersk')

def allPartialResults():
	for center in centers:
		partialResult(center)

def VerifyZKP(center):
	if not os.path.exists('pysnark_values_' + str(center)) or not os.path.exists('pysnark_proof_' + str(center)):
		print(f'Skipping center {center}: missing data.')
		return
	#rename file
	prepareFiles(center)
	#run verification
	print(f'Verification for the center No. {center}: ', end='')
	try:
		verify()
		print('success!')
		partialData = loadData()
		if partialData[1]: 
			print("The trusted results are:")
			showData(partialData)
		else:
			print('    Nobody has voted yet.')
	except Exception as e:
		print(e)
	#rename file back
	storeFiles(center)


def VerifyAllZKP():
	for center in centers:
		VerifyZKP(center)

def finalResult():
	results = [0, 0, 0, 0]
	for center in centers:
		if not os.path.exists('pysnark_values_' + str(center)) or not os.path.exists('pysnark_proof_' + str(center)):
			print(f'Missing data for center {center}. Can\'t compute final results.')
			return
		prepareFiles(center)
		results = [results[i] + d for i, d in enumerate(loadData())]
		storeFiles(center)
	#show data
	print('Final results:')
	showData(results)


try:
	with cx_Oracle.connect(user=username, password=password,
	dsn='localhost/xe') as connection:
		print('Connection success')
		print('Welcome to admin utility for voting!')
		action = ''
		while action != '4':
			action = input(
				'Please choose: \n'
				'1 to compute partial results, \n'
				'2 to verify computed results with ZKP, \n'
				'3 to get final results, \n'
				'4 for exit: \n')
			if action == '1':
				allPartialResults()
			if action == '2':
				VerifyAllZKP()
			if action == '3':
				finalResult()
				
except cx_Oracle.DatabaseError:
	print("Failed to connect to DB, check login and password")

