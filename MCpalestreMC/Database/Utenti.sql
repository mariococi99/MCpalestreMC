create user 'anonimo'@'localhost' identified with mysql_native_password by 'anonimo';
CREATE ROLE Anonimo;
GRANT Anonimo to 'anonimo'@'localhost';

create user 'cliente'@'localhost' identified with mysql_native_password by 'cliente';
CREATE ROLE Cliente;
GRANT Cliente to 'cliente'@'localhost';

create user 'istruttore'@'localhost' identified with mysql_native_password by 'istruttore';
create user 'gestore'@'localhost' identified with mysql_native_password by 'gestore';

CREATE ROLE Istruttore;
CREATE ROLE Gestore;

GRANT Istruttore to 'istruttore'@'localhost';utenti
GRANT Gestore to 'gestore'@'localhost';