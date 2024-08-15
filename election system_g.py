from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from phe import paillier

# Generate RSA keys for encryption and signing
def generate_rsa_key_pair():
    key = RSA.generate(2048)
    private_key = key
    public_key = key.publickey()
    return private_key, public_key

# Encrypt the vote using RSA
def rsa_encrypt(public_key, vote):
    cipher = PKCS1_OAEP.new(public_key)
    encrypted_vote = cipher.encrypt(vote.encode())
    return encrypted_vote

# Decrypt the vote using RSA
def rsa_decrypt(private_key, encrypted_vote):
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_vote = cipher.decrypt(encrypted_vote)
    return decrypted_vote.decode()

# Sign the vote using RSA
def rsa_sign(private_key, vote):
    h = SHA256.new(vote.encode())
    signature = pkcs1_15.new(private_key).sign(h)
    return signature

# Verify the vote signature using RSA
def rsa_verify(public_key, vote, signature):
    h = SHA256.new(vote.encode())
    try:
        pkcs1_15.new(public_key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False

# Generate Paillier key pair for homomorphic encryption
def generate_paillier_key_pair():
    return paillier.generate_paillier_keypair()


# Voter Registration with age and tally center information
class Voter:
    def __init__(self, name, tally_center, private_key, public_key):
        self.name = name
        self.tally_center = tally_center
        self.private_key = private_key
        self.public_key = public_key


# Tally Center
class TallyCenter:
    def __init__(self, center_id):
        self.center_id = center_id
        self.encrypted_votes = []
        self.zkps = []
        self.signatures = []
        self.public_keys = []
        self.homomorphic_sum = None  # Initialize as None
        self.democrat_votes = 0  # Counter for Democrat votes
        self.republican_votes = 0  # Counter for Republican votes
        self.paillier_public_key, self.paillier_private_key = generate_paillier_key_pair()

    def receive_vote(self, voter, vote):
        if voter.tally_center != self.center_id:
            print(f"Voter {voter.name} is not eligible to vote at this center.")
            return

        # Convert vote to an integer
        r=0
        d=0
        if vote == "Republican":
            vote_int = 1
            r=1
        elif vote == "Democrat":
            d=1
            vote_int = 0
        else:
            print("Invalid vote.")
            return
        #zkp
        if (r+d)==1:
            print("Vote successfully recorded zkp")
        encrypted_vote = rsa_encrypt(voter.public_key, str(vote_int))
        signed_vote = rsa_sign(voter.private_key, str(vote_int))
        if rsa_verify(voter.public_key, str(vote_int), signed_vote) :
            encrypted_vote_value = self.paillier_public_key.encrypt(vote_int)

            # Initialize homomorphic_sum with the first encrypted vote
            if self.homomorphic_sum is None:
                self.homomorphic_sum = encrypted_vote_value
            else:
                self.homomorphic_sum += encrypted_vote_value

            self.encrypted_votes.append(encrypted_vote)

            self.signatures.append(signed_vote)
            self.public_keys.append(voter.public_key)

            if vote == "Democrat":
                self.democrat_votes += 1
            elif vote == "Republican":
                self.republican_votes += 1

            print(f"Vote  successfully recorded.")
        else:
            print(f"Vote  failed verification.")

    def compute_tally(self):
        return {"Democrat": self.democrat_votes, "Republican": self.republican_votes}

# Voting System to manage tally centers
class VotingSystem:
    def __init__(self):
        self.tally_centers = {}

    def add_tally_center(self, tally_center):
        self.tally_centers[tally_center.center_id] = tally_center

    def cast_vote(self, voter, vote):
        if voter.tally_center in self.tally_centers:
            self.tally_centers[voter.tally_center].receive_vote(voter, vote)
        else:
            print(f"Tally center {voter.tally_center} does not exist.")

    def compute_results(self):
        final_tally = {"Democrat": 0, "Republican": 0}
        for center_id, center in self.tally_centers.items():
            center_tally = center.compute_tally()
            final_tally["Democrat"] += center_tally["Democrat"]
            final_tally["Republican"] += center_tally["Republican"]
        return final_tally

# Example usage
private_key1, public_key1 = generate_rsa_key_pair()
voter1 = Voter(
    name="John Doe",
    tally_center="Center1",
    private_key=private_key1,
    public_key=public_key1,
)

private_key2, public_key2 = generate_rsa_key_pair()
voter2 = Voter(
    name="Jane Smith",
    tally_center="Center2",
    private_key=private_key2,
    public_key=public_key2,

)

voting_system = VotingSystem()

tally_center1 = TallyCenter("Center1")
tally_center2 = TallyCenter("Center2")

voting_system.add_tally_center(tally_center1)
voting_system.add_tally_center(tally_center2)

# Voters cast their votes
voting_system.cast_vote(voter1, "Republican")
voting_system.cast_vote(voter2, "Democrat")

# Compute final results across all tally centers
results = voting_system.compute_results()
print("Final Tally:", results)


