
from hashlib import scrypt

with open('salt.txt', 'r') as saltFile:
	salt = saltFile.read()
def getVotersToBd(Voters):
	for voter in Voters:
		hashkey=scrypt((voter).encode(),
				  salt=salt.encode(), n=16384, r=8, p=1)
		print (hashkey)
	print()



Voters1 = ["AlexIvanov123456789", "MaryPetrova234567890", "IvanSmirnov345678901", "OlgaKuznetzova456789012",
           "DmitriyVolkov567890123"]
Voters2 = ["ElenaFedorova678901234", "AndreyPopov789012345", "AnnVasilieva890123456", "MihailMorozov901234567",
           "TatianaSergeeva"]
Voters3 = ["VladimirLebedev213456789", "IrinaSidorova324567890", "SergeyGrigoriev435678901", "NataliaBelova546789012",
           "UriTihonov657890123"]


getVotersToBd(Voters1)
getVotersToBd(Voters2)
getVotersToBd(Voters3)
