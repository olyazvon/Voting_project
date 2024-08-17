#THE MAIN MANAGEMENT SCRIPT

import cx_Oracle
from hashlib import scrypt

#Globals

username = 'election_admin'
password = '1234'
with open('salt.txt', 'r') as saltFile:
	salt = saltFile.read()

#Functions

def getNewVoter():
	voterName = input("Voter name: ")
	voterSurname = input("Voter surname: ")
	voterID = input("Voter ID: ")
	voterCenter = input("Voter tally center: ")
	return scrypt((voterName+voterSurname+voterID).encode(), 
		salt=salt.encode(), n=16384, r=8, p=1), voterCenter

def addVoterQuery(hashkey, center, connection):
	cursor = connection.cursor()
	cursor.execute("INSERT INTO Voters (hashKey, tallyCenter) VALUES (:hash, :center)",
		hash=hashkey, center=center)
	connection.commit()

def showStatistics():
	pass
	#TODO: implement


print('Welcome to admin utility for voting!')

with cx_Oracle.connect(user=username, password=password, 
	dsn='localhost/xe') as connection:
	print('Connection success')

	action = ''
	while action != '3':
		action = input('Enter 1 to add a new voter, 2 for current statistics, 3 for exit: ')
		if action == '1':
			a = getNewVoter()
			addVoterQuery(*a, connection)
		if action == '2':
			showStatistics()