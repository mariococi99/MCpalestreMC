create user 'anonimo'@'localhost' identified with mysql_native_password by 'anonimo';
CREATE ROLE Anonimo;
GRANT Anonimo to 'anonimo'@'localhost';

create user 'cliente'@'localhost' identified with mysql_native_password by 'cliente';
CREATE ROLE Cliente;
GRANT Cliente to 'cliente'@'localhost';