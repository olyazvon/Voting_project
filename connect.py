import cx_Oracle
from hashlib import scrypt
import random
print('import succeeded')

# Задайте параметры подключения
username = 'election_admin'
password = '1234'
hostname = 'localhost'    # Например, 'localhost' или IP-адрес
port = 1521       # Обычно 1521
sid = 'xe'          # SID базы данных
# Создание DSN
dsn = cx_Oracle.makedsn(hostname, port, sid=sid)

# Подключение к базе данных
connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)

# Создание курсора
cursor = connection.cursor()

un = input("Введите имя пользователя: ").encode()
us = input("Введите фам пользователя: ").encode()
id = input("Введите id пользователя ").encode()
# нужна функция  проверки ввода
hashkey = scrypt(un+us+id,
    salt='we can just use some string stored outside of DB'.encode(),
    n=16384, r=8, p=1)
hashuser=hashkey.hex()
print(hashuser)

centers=(1,2,3)
# Выполнение SQL-запроса
#cursor.execute("CREATE TABLE Voters(name  VARCHAR2(128) UNIQUE, center INTEGER,isVoted varchar2 (5) not null, constraint chk_tab_bool2 check (isVoted IN ('true','false')))")
cursor.execute("INSERT INTO Voters(name, center,isVoted) VALUES (:1, :2,:3)", (hashuser,random.choice(centers),'false'))
#cursor.execute("INSERT INTO Voters(name, center) VALUES('SHDKHKDjoi',2)")
cursor.execute("SELECT * FROM Voters")
connection.commit()
# Получение и вывод результата
for row in cursor:
    print(row)

# Закрытие курсора и соединения
cursor.close()
connection.close()

