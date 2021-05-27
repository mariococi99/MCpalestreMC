CREATE TABLE palestre(
idpalestra INT,
indirizzo VARCHAR(30),
email VARCHAR(30),
telefono VARCHAR(15),
cf VARCHAR(17)
);
CREATE TABLE utenti(
cf VARCHAR(17),
nome VARCHAR(15),
cognome VARCHAR(15),
email VARCHAR(30),
telefono VARCHAR(15),
tampone BIT,
tipo ENUM('gestore', 'istruttore', 'fruitore'),
idpalestra INT
);
CREATE TABLE locali(
idlocale VARCHAR(30),
mq INT,
idpalestra INT
);
CREATE TABLE corsi(
idcorso INT,
istruttore VARCHAR(17),
titolo VARCHAR(50),
personemax INT,
descrizione VARCHAR(100),
idlocale VARCHAR(30)
);
CREATE TABLE prenotazioni(
cf VARCHAR(17),
idcorso INT,
orario DATETIME
)