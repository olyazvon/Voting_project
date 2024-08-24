## Voting System with Encryption and Verification

#### Description

This project is a comprehensive voting system designed to ensure the confidentiality and integrity of votes using cryptographic methods. The system comprises two main components:

1. **User Script (Voting Interface):**
   - Allows voters to cast their votes
   - Checks their eligibility
   - Stores encrypted votes in Database
2. **Admin Script (Result Management):**
   - Computes partial voting results
   - Verifies the correctness of calculations using Zero-Knowledge Proofs (ZKP)
   - Provides the final voting results

#### Key Components

1. **Cryptographic Methods:**
   - **Paillier Encryption:** Used to protect votes and ensure their confidentiality.
   - **Hashing (scrypt):** Used to verify voter identity and ensure uniqueness of records.

2. **Database :**
   - Used Oracle database for  storing, and retrieving voting and voter data.
3. **ZKP :**
   - Used pysnark with backend qaptools (add files from: https://github.com/Charterhouse/qaptools)

5. **User Interface:**
   - **Text-Based Interface:** Provides an interface for both administrators and voters to interact with the system.

#### Main Workflow

1. **For the Administrative Script:**
   - **Initialization:** Load encryption keys and prepare the environment.
   - **Partial Results Calculation:** Process data for each voting center.
   - **Correctness Verification:** Use Zero-Knowledge Proofs to verify the results.
   - **Final Results Computation:** Aggregate partial results and display the final voting outcome.

2. **For the User Script:**
   - **Initialization:** Connect to the database and request necessary data.
   - **Start of voting:** Admin connect to DB and add voter center
   - **Data Input:** Verify and hash the voter’s personal data.
   - **Voting Process:** Encrypt and store the vote in the database.
   - **Error Handling and Completion:** Verify the success of saving the vote and provide feedback.

This project offers a robust solution for conducting and managing elections, leveraging modern cryptographic techniques and verification processes to ensure the security and integrity of voting data.
