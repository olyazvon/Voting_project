# THE MAIN MANAGEMENT SCRIPT

import cx_Oracle
import os
from phe import paillier
from pysnark.qaptools.runqapver import run as verify
from random import SystemRandom
from subprocess import run, DEVNULL


# Constants

MAX_VOTERS = 10000
centers = (1, 2, 3)
# TODO  удалить перед сдачей:
username = 'election_admin'
password = '1234'


# Functions

def catchMissingFile(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            filename = e.filename if hasattr(e, 'filename') else 'unknown'
            print(f"File {filename} not found, can't continue.")
            exit()
    return wrapper

@catchMissingFile
def readFile(filename):
	with open(filename, encoding='utf-8') as file:
			contents = file.read()
	return contents

@catchMissingFile
def storeFiles(center):
	if os.path.exists('pysnark_values_' + str(center)):
		os.remove('pysnark_values_' + str(center))
	os.rename('pysnark_values', 'pysnark_values_' + str(center))
	if os.path.exists('pysnark_proof_' + str(center)):
		os.remove('pysnark_proof_' + str(center))
	os.rename('pysnark_proof', 'pysnark_proof_' + str(center))

@catchMissingFile
def prepareFiles(center):
	if os.path.exists('pysnark_values'):
		os.remove('pysnark_values')
	os.rename('pysnark_values_' + str(center), 'pysnark_values')
	if os.path.exists('pysnark_proof'):
		os.remove('pysnark_proof')
	os.rename('pysnark_proof_' + str(center), 'pysnark_proof')

@catchMissingFile
def loadData():
	with open('pysnark_values') as f:
		l = f.readlines()
		return [int(l[i].split(' ')[-1][:-1]) for i in (1, 2, -2, -1)]

def showData(data):
	allVoters, votedVoters, dVotes, rVotes = data
	print(f'    Voted: {votedVoters}/{allVoters} ({votedVoters/allVoters*100:.2f}%)')
	print(f'    Respublicans: {rVotes/votedVoters*100:.2f}%, Democrats: {dVotes/votedVoters*100:.2f}%')

@catchMissingFile
def deleteExtraFiles():
	os.remove('pysnark_eqs')
	os.remove('pysnark_wires')
	if os.path.exists('pysnark_mastersk'):
		os.remove('pysnark_mastersk')

def partialResult(center, connection):
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
	obf = SystemRandom().randrange(1, 150)
	votes.append(public_key.encrypt(0, r_value=obf))

	print(f'In the center No. {center}:')

	#sum votes
	encryptedSum = sum(votes).ciphertext()

	#zkp decrypt
	retCode = run(['python', 'decrypt.py', str(encryptedSum), str(allVoters), str(votedVoters)], 
		stdout=DEVNULL, stderr=DEVNULL).returncode
	if retCode != 0:
		print('The decryption subprocess terminated with an error. Decryption was not performed.')

	if votedVoters == 0:
		print("    Nobody has voted yet.")
	else:
	#load data
	#show data
		showData(loadData())

	#file rename
	storeFiles(center)

	#del extra files
	deleteExtraFiles()

def allPartialResults(connection):
	for center in centers:
		partialResult(center, connection)

def VerifyZKP(center):
	if (not os.path.exists('pysnark_values_' + str(center)) or 
		not os.path.exists('pysnark_proof_' + str(center))):
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
	if (not os.path.exists('pysnark_schedule') or
		not os.path.exists('pysnark_masterpk') or
		not os.path.exists('pysnark_vk_main')):
		print("Missing global computational data, can't verify.")
		return
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
	if results[1] == 0:
		print("    Nobody has voted.")
	else:
		showData(results)


def main():
	username = input("Input username: ")
	password = input("Input password: ")

	with cx_Oracle.connect(user=username, password=password,
	dsn='localhost/xe') as connection:
		print('Connection success')
		print('Welcome to admin utility for voting!')
		action = ''
		while True:
			action = input(
				'\nPlease choose: \n'
				'1 to compute partial results, \n'
				'2 to verify computed results with ZKP, \n'
				'3 to get final results, \n'
				'4 for exit: \n')
			print()
			if action == '1':
				allPartialResults(connection)
			if action == '2':
				VerifyAllZKP()
			if action == '3':
				finalResult()
			if action == '4':
				exit()


# Main flow

try:
	n = int(readFile('paillier_public_key.txt'))
	lines = readFile('paillier_private_key.txt').split("\n")
	p = int(lines[0])
	q = int(lines[1])
	public_key = paillier.PaillierPublicKey(n)
	private_key = paillier.PaillierPrivateKey(public_key, p, q)
except:
	print("Wrong paillier keys structure.")
	exit()

while True:
	try:
		main()				
	except cx_Oracle.DatabaseError as exc:
		error_code = exc.args[0].code
		if error_code == 1017:
			print("Invalid username or password.")
		elif error_code == 28000:
			print("User is locked.")
		else:
			print("Database error:", exc)
	except KeyboardInterrupt:
		print("\nStopped with Ctrl-C")
		break

