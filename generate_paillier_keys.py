from phe.paillier import generate_paillier_keypair

pubKey, privKey = generate_paillier_keypair(n_length=256)

with open('paillier_public_key.txt', 'w') as f:
	f.write(str(pubKey.n)+'\n')

with open('paillier_private_key.txt', 'w') as f:
	f.writelines((str(privKey.p)+'\n', str(privKey.q)+'\n'))
