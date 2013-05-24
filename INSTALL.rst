INSTALL instruction

* Install django and its requirements: `pip install -r requirements.txt`
* Download nltk data: in python, type
  `import nltk`
  `nltk.download()`
** Configure the download path to `/usr/local/share/nltk_data`
** Download `wordnet`

* MySQL configuration

** MySQL configuration issues

MySQL must be configured to correctly handle utf8. According to
http://mathiasbynens.be/notes/mysql-utf8mb4 , utf8mb4 is preferable to
avoid being bitten by obscure characters.

- configure mysql server with (on Debian, create a file in in ``/etc/mysql/conf.d/``)

  [client]
  default-character-set = utf8mb4
  
  [mysql]
  default-character-set = utf8mb4
  
  [mysqld]
  character-set-client-handshake = FALSE
  character-set-server = utf8mb4
  collation-server = utf8mb4_unicode_ci

- create database with the SQL command

  create database kadist DEFAULT CHARACTER SET utf8mb4;
