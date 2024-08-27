## Voting System with Encryption and ZKP Verification

#### Description

This is a study project, implementing a comprehensive voting system designed to ensure the confidentiality and integrity of votes using cryptographic methods. The system comprises two main components:

1. **User Script (Voting Interface):**
   - Allows voters to cast their votes
   - Checks their eligibility
   - Stores encrypted votes in database

2. **Admin Script (Result Management):**
   - Computes partial voting results
   - Verifies the correctness of decryption using Zero-Knowledge Proofs (ZKP)
   - Provides the final voting results

#### Key Features

1. **Cryptographic Methods:**
   - **Paillier Encryption:** Used to protect votes and ensure their confidentiality.
   - **Hashing (scrypt):** Used to securely verify voter identity.

2. **ZKP :**
   - pysnark with qaptools backend to сonfirm that the reported results are correctly tallied.

3. **Database :**
   - We use Oracle database to store all the data.

#### How does it work?

1. **The Administrative Script:**
   - **Initialization:** load encryption keys and prepare the environment.
   - **Partial Results Calculation:** process data for each voting center. Get all the votes, sum them, using the properties of Paillier encryption, then decrypt the sum.
   - **Correctness Verification:** use Zero-Knowledge Proofs to verify the decryption.
   - **Final Results Computation:** aggregate partial results and display the final voting outcome.

2. **The User Script:**
   - **Initialization:** admin connect to DB and add specify the No. of the voting center
   - **Personal Data Input:** get and hash the voter’s personal data.
   - **Voter Check:** send SQL-request to chak whether voter can vote here and now.
   - **Voting Process:** get the vote, encrypt and store the vote in the database.
   - **Vote check:** Verify the success of saving the vote and indicate it.
   - **Loop to Data Input:** The voting center is ready to welcome a new visitor.


#### Note

This project contains Windows executables qapcoeffcache.exe, qapgen.exe, qapgenf.exe, qapinput.exe, qapprove.exe and qapver.exe. These files don't belong to us. 
Copyright (c) 2016-2018 Koninklijke Philips N.V. (see LICENSE file).
Source: https://github.com/Charterhouse/qaptools

File `decrypt.py` contains modified code from the phe library by CSIRO Data61 Engineering & Design.
Source: https://github.com/data61/python-paillier

