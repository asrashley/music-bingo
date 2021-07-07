# Database

Both the application and the server use a database to store the list of
available clips and details of each generated game. By default they use
a file called "bingo.db3" which contains an sqlite database.

Other databases can be used, such as mariadb, mysql or SQL server. Any
database engine that is supported by
[SQLAlchemy](https://docs.sqlalchemy.org/en/13/) can be used.

The simplest way to change which database engine is used is to edit
the "bingo.ini" file and look for the [database] section

    [database]
    provider = sqlite
    name = C:\Users\Alex\source\music-bingo\bingo.db3
    create_db = True
    ssl = null

The "provider" settings is the database engine to use. See
[Engine Configuration](https://docs.sqlalchemy.org/en/13/core/engines.html)
for more information on possible engines.

## Mysql or mariadb

An example of using mysql or mariadb:

    [database]
    provider = mysql
    host = localhost
    name = bingo
    create_db = True
    user = bingouser
    passwd = mysecret

You will also need to install the Python mysql driver:

    pip install -r mysql-requirements.txt

To create the database and grant access to the bingo application:

    CREATE DATABASE bingo;
    CREATE USER 'bingouser'@'localhost';
    GRANT ALL ON bingo.* TO 'bingouser'@'localhost' IDENTIFIED BY "mysecret";
    FLUSH PRIVILEGES;

**Please don't use mysecret as your database password!**

## sqlserver

An example of using SQL server:

    [database]
    provider = mssql+pyodbc
    host = localhost
    name = bingo
    create_db = True
    user = bingouser
    passwd = mysecret
    driver = SQL Server Native Client 11.0

This needs the Python ODBC driver:

    pip install pyodbc
