DROP TABLE Voters;

CREATE TABLE Voters
(
	hashKey RAW(64) PRIMARY KEY,
	tallyCenter NUMBER(2),
	vote CHAR(64 BYTE) DEFAULT NULL
);

INSERT INTO Voters (hashKey, tallyCenter)
VALUES (HEXTORAW('aa04c6a82c56700d95d1411c497e0c764d2581422fdef5aca62358f855257a42e330745717c9e676cecb399d895bf9d455f964bfe3a5d498f4f47a3d4a8d5aa1'), 1);
-- Name: m, Surname: s, ID: 1, salt: this is the salt for scrypt function