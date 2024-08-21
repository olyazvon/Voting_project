# THE MAIN MANAGEMENT SCRIPT

import cx_Oracle
from hashlib import scrypt

# Globals

username = 'election_admin'
password = '1234'
with open('salt.txt', 'r') as saltFile:
	salt = saltFile.read()

# Functions

def getNewVoter():
	voterName = input("Voter name: ")
	voterSurname = input("Voter surname: ")
	voterID = checkId()
	voterCenter = input("Voter tally center: ")
	return scrypt((voterName+voterSurname+voterID).encode(), 
		salt=salt.encode(), n=16384, r=8, p=1), voterCenter

def checkId():
	voterID = input("Voter ID: ")
	while (not voterID.isdigit) or len(voterID) != 9:
		voterID = input("ID must consist of 9 digits. Try again: ")
	return(voterID)
def getVotersToBd(Voters,voterCenter,conection):
	for voter in Voters:
		hashkey=scrypt((voter).encode(),
				  salt=salt.encode(), n=16384, r=8, p=1)
		addVoterQuery(hashkey,voterCenter,conection)

def addVoterQuery(hashkey, center, connection):
	cursor = connection.cursor()
	cursor.execute(
		'''INSERT INTO Voters (hashKey, tallyCenter)
		VALUES (:hash, :center)''',
		hash=hashkey, center=center)
	connection.commit()


def showStatistics(center):
	cursor = connection.cursor()
	cursor.execute('''SELECT COUNT(*), COUNT(vote) FROM Voters''')
	allVoters, votedVoters = cursor.fetchone()
	cursor.execute('''SELECT SUM(vote) FROM Voters''')
	rVotes, dVotes = divmod(cursor.fetchone()[0], 100000000)
	#print(f'Current results in the center No. {center}:')
	print(f'Voted: {votedVoters}/{allVoters} ({votedVoters/allVoters*100:.2f}%)')
	print(f'Respublicans: {rVotes/votedVoters*100:.2f}%, Democrats: {dVotes/votedVoters*100:.2f}%')
	# TODO: restrict access to one center results


print('Welcome to admin utility for voting!')
# Voters1 = ["AlexIvanov123456789", "MaryPetrova234567890", "IvanSmirnov345678901", "OlgaKuznetzova456789012","DmitriyVolkov567890123"]
# Voters2 = ["ElenaFedorova678901234", "AndreyPopov789012345", "AnnVasilieva890123456", "MihailMorozov901234567","TatianaSergeeva"]
# Voters3 = ["VladimirLebedev213456789", "IrinaSidorova324567890", "SergeyGrigoriev435678901", "NataliaBelova546789012","UriTihonov657890123"]

centerNumber = int(input('Input the tally center number: '))

with cx_Oracle.connect(user=username, password=password, 
	dsn='localhost/xe') as connection:
	print('Connection success')

	# getVotersToBd(Voters1,1,connection)
	# getVotersToBd(Voters2, 2, connection)
	# getVotersToBd(Voters3, 3, connection)


	action = ''
	while action != '3':
		action = input('Enter 1 to add a new voter, 2 for current statistics, 3 for exit: ')
		if action == '1':
			a = getNewVoter()
			addVoterQuery(*a, connection)
		if action == '2':
			showStatistics(centerNumber)
