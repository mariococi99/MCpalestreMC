"""
Questi import servono per far funzionare interamente l'applicazione web
"""
import datetime
from datetime import *
import calendar
from flask import render_template, url_for, request, flash, session, redirect, Blueprint
from flask_bootstrap import Bootstrap
from MCpalestreMC import app
from MCpalestreMC.forms import *
import sqlalchemy
from sqlalchemy import *
import flask_login
from flask_login import LoginManager, login_required, login_user, UserMixin, login_manager, logout_user, current_user

"""
Setting che inizializzano la secret key flash
"""
app.config['SECRET_KEY'] = 'bgit4y5394rjfienvtn8'
login_manager = LoginManager()
login_manager.init_app(app)
bootstrap = Bootstrap(app)

"""
Mi collego al dbms come utente anonimo
Creo l'engine(collegamento al dbms) globale
Attivo i ruoli sul database
"""
uri = 'mysql://anonimo:anonimo@localhost/mcpalestremc' #uri per collegarsi al dbms
engine = create_engine(uri) #crea il collegamento con il dbms
conn = engine.connect()
conn.execute("set global activate_all_roles_on_login = on") #attivazione ruoli
conn.close()

"""
Variabile che conterrà la data in caso di necessità 
"""
today = datetime.today().strftime('%Y-%m-%d')

"""
Classe che viene usata per contenere i dati di un utente generico
"""
class User (UserMixin):
    """
    Costruttore
    """
    def __init__ (self, cf, nome, cognome, email, numero, pwd, tampone, tipo, palestra):
        self.cf = cf
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.numero = numero
        self.pwd = pwd
        self.tampone = tampone
        self.tipo = tipo
        self.palestra = palestra
    
    """
    Questa funzione ritorna il tipo di utente tra Istruttore, Gestore e Cliente
    """
    def get_tipo(self):
        return self.tipo

    """
    Questa funzione ritorna il codice fiscale dell'utente
    """
    def get_id(self):
        return self.cf

    """
    Questa funzione ritorna l'id della palestra a cui ha accesso l'utente
    """
    def get_palestra(self):
        return self.palestra
    """
    Questa funzione ritorna l'ultimo tampone dell'utente
    """
    def get_tampone(self):
        return self.tampone


"""
Questa funzione serve per vedere se l'utente è loggato o meno
Visto che il passaggio di dati da javascript a python può sollevare problemi,
si è preferito scrivere una funzione per risolvere la questione
"""
def is_logged():
    if current_user.is_authenticated:
        return 'true'
    return 'false'

"""
Questa funzione serve per ricavare tutte le date disponibili tra due
date iniziali e finali, dato un certo giorno della settimana.
Il formato delle date è %YYYY-%MM-%DD
"""
def date_disponibili(inizio, fine, giorno):
    date = []
    days_week = ['Lunedì', 'Martedi', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    data = datetime.strptime(inizio, '%Y-%m-%d').date()

    while str(days_week[data.weekday()]) != giorno:
        data = data + timedelta(days = 1)

    while str(data) <= fine :
        date.append(data)
        data = data + timedelta(weeks = 1)

    return date

"""
Questa funzione serve per eliminare eventuali date che non sono necessarie
"""
def date_rimanenti(origine, rimozione):
    date = []
    for i in origine:
        date.append(str(i))

    date_finali = []
    for i in date:
        if i not in rimozione:
            date_finali.append(datetime.strptime(i, '%Y-%m-%d').date())
    
    date_definitive = []

    todayf = datetime.strptime(today, '%Y-%m-%d').date()
    for i in date_finali:
        if i > todayf:
            date_definitive.append(datetime.strptime(str(i), '%Y-%m-%d').date())

    return date_definitive

"""
Funzione che serve per il corretto funzionamento dell'autenticazione.
"""
@login_manager.user_loader
def load_user (user_cf):
    conn = engine.connect()
    s = text("SELECT * FROM utenti u WHERE u.CF =:utente")
    rs = conn.execute(s, utente = user_cf)
    user = rs.fetchone()
    conn.close()
    return User(user.cf, user.nome, user.cognome, user.email, user.numero, user.password, user.tampone, user.tipo, user.idpalestra)

"""
La funzione home ritorna il rendering della pagina principale/iniziale home
"""
@app.route('/', methods = ['GET', 'POST'])
@app.route('/home', methods = ['GET', 'POST'])
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        is_logged = is_logged(),
        title ='Home page',
        year = datetime.now().year,
    )
"""
La funzione about ritorna il rendering della pagina about
"""
@app.route('/about', methods = ['GET', 'POST'])
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        is_logged = is_logged(),
        title = 'La nostra storia - About us',
        year = datetime.now().year,
        message = 'MCpalestreMC nasce come un progetto per la materia base di dati. La proposta di una serie di palestre innovative, nata dal genio di Bill Gates e Topo Gigio nel 2021, ha dato vita a numerose palestre in giro per il mondo che allenano ogni giorno persone e pokemon con una grande forza di volontà. La nostra storia è breve, ma il nostro cuore è grande.'
    )
"""
Se non viene premuto il pulsante di invio, la funzione renderizzerà l'html della stessa.
Quando il form viene inviato, si prendono i campi del codice fiscale e si chiede alla basi di dati
un utente con codice fiscale uguale e password uguale. Se i campi corrispondono entrambi, si instanzia
una classe User con tutti i dati dell'utente, (che saranno utili per tutta la durata dell'utilizzo del sito),
poi si crea l'engine per l'utente; fatto ciò ci sarà il redirect dell'area riservata.
Se codice fiscale o password non coincidono con quelli del dbms o di errore nel try, 
la pagina di login vien ricaricata.
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    global engine
    form = LoginForm()
    if form.is_submitted():
        result = request.form
        try:
            cf = result['cf'].upper()
            password = result['password']

            conn = engine.connect()
            t = text('SELECT * FROM utenti u WHERE u.CF =:cf AND u.Password =:password')
            f = conn.execute(t, cf = cf, password = password).fetchone()
            conn.close()
            if f:
                user = User(f['cf'], f['nome'], f['cognome'], f['email'], f["numero"], f['password'], f['tampone'], f['tipo'], f['idpalestra'])
                login_user(user)
                engine = create_engine("mysql://" + cf + ":" + password + "@localhost/mcpalestremc")
                return redirect(url_for('area_riservata'))
            else:
                flash("Errore durante l'accesso: hai sbagliato codice fiscale o password", "error")
                return redirect(url_for("login"))
        except:
            conn.close()
            flash("Errore durante l'accesso", 'error')
            return redirect(url_for('login'))
    return render_template(
        "login.html",
        is_logged = is_logged(),
        title = 'Login',
        year = datetime.now().year,
        form = form
        ) 

"""
Quando un utente autenticato vuole fare logout, premera' l'input "Logout" e verra'
rimandato alla home page, per la quale non serve autenticazione. Si fa riferimento
all'engine globale e si richiama flask-login per fare il logout.
"""
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    global engine
    engine = create_engine('mysql://anonimo:anonimo@localhost/mcpalestremc')
    logout_user()
    return redirect(url_for('home')) 

"""
La funzione renderizza il template della pagina in caso non ci sia alcun invio.
In alternativa, prende i parametri che serviranno alla registrazione dell'utente,
settando una transazione di livello serializable. Si chiede alla base di dati di 
ritornare un utente con cf identico a quello passato. Se non si ritorna niente,
si fa il commit e si ristampa la stessa pagina, sennò si inserisce il neo utente
nella tabella dandogli i privilegi giusti, poi si va alla pagina di login.
"""
@app.route('/registrazione', methods=['GET', 'POST'])
def registrazione():
    try:
        conn = engine.connect()
        conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        conn.execute("START TRANSACTION")
        s = text("SELECT idpalestra FROM palestre ")
        idpalestre = conn.execute(s)
        palestre = []
        for p in idpalestre:
            palestre.append(p[0])
        form = RegistrationForm(palestre)
        if form.is_submitted():
            result = request.form

            cf = result['cf'].upper()
            nome = result['nome']
            cognome = result['cognome']
            email = result['email']
            numero = result['numero']
            password = result['password']
            palestra = result['palestra']
            
            s = text("SELECT u.CF FROM utenti u WHERE u.CF =:cf")
            id = conn.execute(s, cf = cf).fetchone()
            
            if id:
                conn.execute("COMMIT")
                conn.close()
                flash('Errore: codice fiscale già registrato','error')
                return redirect(url_for('registrazione'))

            s = text("INSERT INTO utenti VALUES(:cf, :nome, :cognome, :email, :numero, :password, 'Negativo', 'Cliente', :palestra)")
            rs = conn.execute (s, cf = cf, nome = nome, cognome = cognome, email = email, numero = numero, password = password, palestra = palestra)
            s = text("create user :codice@'localhost' identified with mysql_native_password by :password")
            rs = conn.execute (s, codice = cf, password = password)

            s = text("GRANT Cliente to :codice@'localhost'")
            rs = conn.execute(s, codice = cf)

            rs = conn.execute("FLUSH PRIVILEGES")
            conn.execute("COMMIT") 
            conn.close()
            return redirect(url_for('login'))
        conn.close()
        return render_template(
            "registrazione.html",
            is_logged = is_logged(),
            title = 'Registrazione',
            year = datetime.now().year,
            form = form
        )
    except:
        conn.execute("ROLLBACK")
        conn.close()
        flash("Errore durante la registrazione", 'error')
        return redirect(url_for('registrazione'))

"""
La funzione serve ad inserire un nuovo utente di tipo istruttore.
Si setta la transazione a livello serializable per avere a disposizione tutte le palestre, 
poi tramite il form si registra un utente con ruolo istruttore in una delle palestre disponibili
"""
@app.route('/registra_istruttore', methods=['GET', 'POST'])
@login_required
def registra_istruttore():
    if current_user.get_tipo() == 'Gestore':
        
        try:
            conn = engine.connect()
            conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            conn.execute("START TRANSACTION")
            s = text("SELECT idpalestra FROM palestre ")
            idpalestre = conn.execute(s)
            palestre = []
            for p in idpalestre:
                palestre.append(p[0])
            form = InstructorRegistrationForm(palestre)
            
            if form.is_submitted():
                result = request.form

                cf = result['cf']
                nome = result['nome']
                cognome = result['cognome']
                email = result['email']
                numero = result['numero']
                password = result['password']
                palestra = result['palestra']
            
                s = text("SELECT u.CF FROM utenti u WHERE u.CF =:cf")
                id = conn.execute(s, cf = cf).fetchone()
            
                if id:
                    conn.execute("COMMIT")
                    conn.close()
                    flash('Errore: codice fiscale già registrato','error')
                    return redirect(url_for('registra_istruttore'))

                s = text("INSERT INTO utenti VALUES(:cf, :nome, :cognome, :email, :numero, :password, 'Negativo', 'Istruttore', :palestra)")
                rs = conn.execute (s, cf = cf, nome = nome, cognome = cognome, email = email, numero = numero, password = password, palestra = palestra)
            
                s = text("create user :codice@'localhost' identified with mysql_native_password by :password")
                rs = conn.execute (s, codice = cf, password = password)

                s = text("GRANT Istruttore to :codice@'localhost'")
                rs = conn.execute(s, codice = cf)

                rs = conn.execute("FLUSH PRIVILEGES")
                conn.execute("COMMIT")

            conn.close()
            return render_template(
                "registra_istruttore.html",
                is_logged = is_logged(),
                title = 'Registra istruttore',
                year = datetime.now().year,
                form = form
            )
        except:
            conn.execute("ROLLBACK")
            conn.close()
            flash("Errore durante la registrazione", 'error')
            return redirect(url_for('registra_istruttore'))
        
    return redirect(url_for('home'))
"""
La funzione permette in primis di scrollare la pagina, data la quantità di Field.
Si provvede ad inserire un gestore con le sue informazioni, quelle della sua nuova palestra e i locali in essa.
Esiste un Button che permette di aggiungere locali, (che minimo devono essere 2).
Alla fine delle operazioni, se corrette, si andrà a registrare il nuovo Gestore, la palestra e le nuove stanze.
"""
@app.route('/registra_gestore', methods=['GET', 'POST'])
@login_required
def registra_gestore():
    if current_user.get_tipo() == 'Gestore':
        scroll = 'top-navbar'
        
        form = GymManagerRegistrationForm()
            
        if form.is_submitted():
            result = request.form

            if result.get("AddField", False):
                form.locali.append_entry()
                scroll = 'add-new-field'
            else:
                try:
                    cf = result['cf']
                    nome = result['nome']
                    cognome = result['cognome']
                    email = result['email']
                    numero = result['numero']
                    password = result['password']
                    palestra = result['palestra']
                    indirizzo = result['indirizzo']
                    emailPalestra = result['emailPalestra']
                    telefono = result['telefono']
                    locali = []
                    for l in form.locali:
                        locali.append(l)
                    conn = engine.connect()
        
                    conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
                    conn.execute("START TRANSACTION")
                    s = text("SELECT u.CF FROM utenti u WHERE u.CF =:cf")
                    id = conn.execute(s, cf = cf).fetchone()
            
                    if id:
                        conn.execute("COMMIT")
                        conn.close()
                        flash('Errore: codice fiscale già registrato','error')
                        return redirect(url_for('registra_gestore'))

                    s = text("INSERT INTO palestre (titolo, indirizzo, email, telefono) VALUES(:titolo, :indirizzo, :email, :telefono)")
                    rs = conn.execute (s, titolo = palestra, indirizzo = indirizzo, email = emailPalestra, telefono = telefono)
                    s = text("SELECT p.idpalestra FROM palestre p ORDER BY p.idpalestra DESC LIMIT 1")
                    idpalestra = conn.execute(s, cf = cf).fetchone()[0]
                    for l in locali:
                        mq = l['mq'].data
                        personemax = l['personeMax'].data
                        s = text("INSERT INTO locali (mq, personemax, idpalestra) VALUES(:mq, :personemax, :idpalestra)")
                        rs = conn.execute (s, mq = mq, personemax = personemax, idpalestra = idpalestra)

                    s = text("INSERT INTO utenti VALUES(:cf, :nome, :cognome, :email, :numero, :password, 'Negativo', 'Gestore', :idpalestra)")
                    rs = conn.execute (s, cf = cf, nome = nome, cognome = cognome, email = email, numero = numero, password = password, idpalestra = idpalestra)

                    s = text("create user :codice@'localhost' identified with mysql_native_password by :password")
                    rs = conn.execute (s, codice = cf, password = password)
     
                    s = text("GRANT Gestore to :codice@'localhost' WITH ADMIN OPTION")
                    rs = conn.execute(s, codice = cf)
                    rs = conn.execute("FLUSH PRIVILEGES")
                    conn.execute("COMMIT")
                    conn.close()
                except:
                    conn.execute("ROLLBACK")
                    conn.close()
                    flash("Errore durante la registrazione", 'error')
                    return redirect(url_for('registra_gestore'))

        return render_template(
            "registra_gestore.html",
            is_logged = is_logged(),
            title = 'Registra gestore',
            year = datetime.now().year,
            form = form,
            scroll = scroll
        )
            
    return redirect(url_for('home'))


"""
La funzione fa il redirect all'area riservata dell'utente in base al suo tipo
"""
@app.route('/area_riservata', methods=['GET', 'POST'])
@login_required
def area_riservata():
    tipo = current_user.get_tipo()
    if(tipo == 'Gestore'):
        return redirect(url_for('area_gestore'))
    elif(tipo == 'Istruttore'):
        return redirect(url_for('area_istruttore'))
    elif(tipo == 'Cliente'):
        return redirect(url_for('area_cliente'))
    else:
       return redirect(url_for('home'))


"""
La funzione recupera tutte le palestre create con dati del gestore che servono per una più corretta visualizzazione
"""
@app.route('/palestre', methods = ['GET'])
def palestre():
    lista_palestre = []
    try:
        conn = engine.connect()
        s = text("SELECT p.Titolo, p.Indirizzo, p.Email, p.Telefono, u.Nome, u.Cognome FROM palestre p JOIN utenti u ON p.idpalestra = u.idpalestra WHERE u.tipo = 'Gestore'")
        palestre = conn.execute(s)
        conn.close()
        for p in palestre:
            lista_palestre.append(p)
    except:
        conn.close()
        flash('Errore, riprovare','error')
        return redirect(url_for('home'))
    return render_template(
        'palestre.html',
        is_logged = is_logged(),
        title = 'Palestre',
        year = datetime.now().year,
        message = 'Le nostre palestre',
        palestre = lista_palestre
    )

"""
La funzione andrà a recuperare tutte le informazioni relative ai corsi disponibili
"""
@app.route('/corsi', methods = ['GET'])
def corsi():
    lista_corsi = []
    try:
        conn = engine.connect()
        s = text("SELECT c.Idcorso, c.Titolo, u.Nome, u.Cognome, c.Descrizione, c.Idlocale, c.Giorno, c.Orarioinizio, c.Datainizio, c.Datafine, c.Sospeso FROM corsi c NATURAL JOIN utenti u")
        corsi = conn.execute(s)
        conn.close()
        for c in corsi:
            lista_corsi.append(c)
    except:
        conn.close()
        flash('Errore, riprovare','error')
        return redirect(url_for('home'))
    return render_template(
            'corsi.html',
            is_logged = is_logged(),
            title = 'Corsi',
            year = datetime.now().year,
            message = 'Vedi i nostri corsi',
            corsi = lista_corsi
        )
   
"""
La funzione renderizza alla pagina degli abbonamenti
"""
@app.route('/abbonamenti', methods = ['GET'])
def abbonamenti():
    return render_template(
        'abbonamenti.html',
        is_logged = is_logged(),
        title = 'Abbonamenti',
        year = datetime.now().year,
        message = 'Abbonamenti belli'
    )

"""
La funzione, se si è gestori, stampa la propria area riservata e recupera le informazioni relative alla palestra
"""
@app.route('/area_gestore', methods = ['GET'])
@login_required
def area_gestore():
    if (current_user.get_tipo() == 'Gestore'):
        try:
            conn = engine.connect()
            s=text("SELECT p.Titolo, p.Indirizzo, p.Email, p.Telefono, COUNT(u.tipo) AS Personeiscritte FROM palestre p LEFT JOIN utenti u USING (idpalestra) WHERE u.tipo = 'Cliente' AND p.idpalestra =:idpalestra")
            palestra = conn.execute(s, idpalestra = current_user.get_palestra()).fetchone()
            conn.close()
            return render_template(
                'area_gestore.html',
                is_logged = is_logged(),
                title = 'Area riservata | Gestore',
                year = datetime.now().year,
                message = 'Area gestore',
                palestra = palestra
            )
        except:
            conn.close()
            flash('Errore durante la richiesta dei dati della palestra','error')
            return redirect(url_for('home'))
    return redirect(url_for('home'))
    
"""
La funzione stampa l'area riservata dell'istruttore, dandogli la possibilità di eseguire alcune azioni 
"""
@app.route('/area_istruttore', methods = ['GET', 'POST'])
@login_required
def area_istruttore():
    if (current_user.get_tipo() == 'Istruttore'):
        form1 = CovidForm()
        form2 = DeleteCourseForm()
        try:
            conn = engine.connect()
            conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            conn.execute("START TRANSACTION")
            if form2.is_submitted() and 'idcorso' in request.form:
                result = request.form
                idcorso = result['idcorso']
                s = text("DELETE FROM corsi WHERE idcorso =:idcorso")
                conn.execute(s, idcorso = idcorso)
                conn.execute("COMMIT")
                conn.close()
                return redirect(url_for('area_riservata'))
            if form1.is_submitted():
                result = request.form
                if 'covid' in result:
                    s = text("UPDATE utenti SET tampone = 'Positivo' WHERE cf =:cf")
                    conn.execute(s, cf = current_user.get_id())
                else:
                    s = text("UPDATE utenti SET tampone = 'Negativo' WHERE cf =:cf")
                    conn.execute(s, cf = current_user.get_id())
                conn.close()
                return redirect(url_for('area_riservata'))
            s = text("SELECT c.Idcorso, c.Titolo, c.Descrizione, c.Idlocale, c.Giorno, c.Orarioinizio, c.Datainizio, c.Datafine, c.Sospeso, COUNT(i.cf) AS Personeiscritte FROM corsi c LEFT JOIN iscrizioni i ON c.idcorso = i.idcorso WHERE c.CF =:cf AND c.datafine > CURDATE() GROUP BY c.idcorso")
            corsi = conn.execute(s, cf = current_user.get_id())
            lista_corsi = []
            for c in corsi:
                lista_corsi.append(c)
            conn.close()
            return render_template(
                'area_istruttore.html',
                is_logged = is_logged(),
                title = 'Area riservata | Istruttore',
                year = datetime.now().year,
                message = 'Area istruttore',
                corsi = lista_corsi,
                form1 = form1,
                form2 = form2
            )
        except:
            conn.close()
            flash('Errore durante la richiesta dei dati dei corsi','error')
            return redirect(url_for('home'))
    return redirect(url_for('home'))

"""
La funzione stampa l'area riservata del cliente, dandogli la possibilità di alcune azioni, tra cui quella di segnalare di avere 
il covid 
"""
@app.route('/area_cliente', methods = ['GET', 'POST'])
@login_required
def area_cliente():
    if (current_user.get_tipo() == 'Cliente'):
        form1 = CovidForm()
        form2 = UnsubscriptionForm()
        try:
            conn = engine.connect()
            conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            conn.execute("START TRANSACTION")
            if form2.is_submitted() and 'idcorso' in request.form:
                result = request.form
                idcorso = result['idcorso']
                s = text("DELETE FROM iscrizioni WHERE idcorso =:idcorso AND cf =:cf")
                conn.execute(s, idcorso = idcorso, cf = current_user.get_id())
                conn.execute("COMMIT")
                conn.close()
                return redirect(url_for('area_riservata'))
            elif form1.is_submitted():
                result = request.form
                if 'covid' in result:
                    s = text("UPDATE utenti SET tampone = 'Positivo' WHERE cf =:cf")
                    conn.execute(s, cf = current_user.get_id())
                else:
                    s = text("UPDATE utenti SET tampone = 'Negativo' WHERE cf =:cf")
                    conn.execute(s, cf = current_user.get_id())
                conn.close()
                return redirect(url_for('area_riservata'))
            s = text("SELECT c.Idcorso, c.Titolo, u.Nome, u.Cognome, c.Descrizione, c.Idlocale, c.Giorno, c.Orarioinizio, c.Datainizio, c.Datafine, c.Sospeso FROM utenti u NATURAL JOIN corsi c JOIN iscrizioni i USING(idcorso) WHERE i.CF =:cf AND c.datafine > CURDATE()")
            corsi = conn.execute(s, cf = current_user.get_id())
            lista_corsi = []
            for c in corsi:
                lista_corsi.append(c)
            conn.close()
            return render_template(
                'area_cliente.html',
                is_logged = is_logged(),
                title = 'Area riservata | Cliente',
                year = datetime.now().year,
                message = 'Area cliente',
                corsi = lista_corsi,
                form1 = form1,
                form2 = form2
            )
        except:
            conn.close()
            flash('Errore durante la richiesta dei corsi a cui sei iscritto','error')
            return redirect(url_for('area_riservata'))
    else:
        return redirect(url_for('home'))

"""
La funzione permette di modificare l'email, il numero telefonico e la palestra a cui ogni utente è associato
"""
@app.route ('/modifica_profilo', methods=['GET', 'POST'])
@login_required
def modifica_profilo():
    try:
        conn = engine.connect()
        conn.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
        conn.execute("START TRANSACTION")

        s = text("SELECT idpalestra FROM palestre")
        idpalestre = conn.execute(s)
        palestre = []
        for p in idpalestre:
            palestre.append(p[0])
        form = ProfileModificationForm(palestre)
        if form.is_submitted():
            result = request.form
            email = result['email']
            numero = result['numero']
            idpalestra = result['idPalestra']
            s = text("UPDATE utenti SET Email =:email, Numero =:numero, Idpalestra=:idpalestra WHERE CF =:cf")
            conn.execute(s, email = email, numero = numero, idpalestra = idpalestra, cf = current_user.get_id())
            conn.execute("COMMIT")
            conn.close()
            return redirect(url_for('area_riservata'))
    except:
        conn.execute("ROLLBACK")
        conn.close()
        flash('Errore: modifica non riuscita, riprovare','error')
        return redirect(url_for('modifica_profilo'))
    return render_template(
        "modifica_profilo.html",
        is_logged = is_logged(),
        title = 'Modifica profilo',
        year = datetime.now().year,
        message = 'Modifica profilo',
        form = form
    )
"""
La funzione permette di visionare i corsi a cui non si è iscritti e di iscriversi
"""
@app.route('/altri_corsi', methods = ['GET', 'POST'])
@login_required
def altri_corsi():
    if (current_user.get_tipo() == 'Cliente'):
        form = SubscriptionForm()
        if form.is_submitted():
            result = request.form
            idcorso = result['idcorso']
            try:
                conn = engine.connect()
                conn.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
                conn.execute("START TRANSACTION")
                s = text("INSERT INTO iscrizioni (idcorso, cf) VALUES (:idcorso, :cf)")
                print(idcorso)
                conn.execute(s, idcorso = idcorso, cf = current_user.get_id())
                print('5')
                conn.execute("COMMIT")
                print('6')
                conn.close()
                print('7')
                return redirect(url_for('altri_corsi'))
            except:
                conn.execute("ROLLBACK")
                conn.close()
                flash('Qualcosa è andato storto', 'error')
                return redirect(url_for('area_riservata'))
        try:
            conn = engine.connect()
            s = text("SELECT c.Idcorso, c.Titolo, u.Nome, u.Cognome, c.Descrizione, c.Idlocale, c.Giorno, c.Orarioinizio, c.Datainizio, c.Datafine, c.Sospeso FROM corsi c NATURAL JOIN utenti u JOIN locali l USING(idlocale) WHERE l.idpalestra =:idpalestra AND :cf NOT IN (SELECT i.CF FROM iscrizioni i WHERE i.idcorso = c.idcorso) AND c.datafine > CURDATE()")
            corsi = conn.execute(s, idpalestra = current_user.get_palestra(), cf = current_user.get_id())
            conn.close()
            lista_corsi = []
            for c in corsi:
                lista_corsi.append(c)
            
            return render_template(
                'altri_corsi.html',
                is_logged = is_logged(),
                title = 'Altri corsi',
                year = datetime.now().year,
                message = 'Ecco i corsi a cui non sei iscritto:',
                corsi = lista_corsi,
                form = form
            )
        except:
            conn.close()
            flash('Non è stato possibile trovare altri corsi', 'error')
            return redirect(url_for('area_riservata'))
    else:
        return redirect(url_for('home'))
"""
La funzione crea un nuovo corso: si ha bisogno del locale già creato dello slot orario disponibile e delle date di inizio e fine
"""
@app.route('/crea_corso', methods = ['GET', 'POST'])
@login_required
def crea_corso():
    if (current_user.get_tipo() == 'Istruttore'):
        try:
            conn = engine.connect()
            s = text("SELECT idlocale FROM locali WHERE idpalestra =:idpalestra")
            idlocali = conn.execute(s, idpalestra = current_user.get_palestra())
            conn.close()
            locali = []
            for l in idlocali:
                locali.append(l[0])
            form = CourseCreationForm(locali)

            if form.is_submitted():
                result = request.form
                titolo = result['titolo']
                descrizione = result['descrizione']
                datainizio = result['dataInizio']
                datafine = result['dataFine']
                giorno = result['giorno']
                orarioinizio = result['orarioInizio']
                idlocale = result['idLocale']
                try:
                    conn = engine.connect()
                    conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
                    conn.execute("START TRANSACTION")

                    s = text("SELECT c.giorno, c.orarioinizio FROM corsi c WHERE c.idlocale =:idlocale AND ((:datainizio BETWEEN c.datainizio AND c.datafine) OR (:datafine BETWEEN c.datainizio AND c.datafine))")
                    orari = conn.execute(s, idlocale = idlocale, datainizio = datainizio, datafine = datafine)
                    lista_orari = []
                    for o in orari:
                        lista_orari.append(o)

                    selezionato = (giorno, orarioinizio)

                    if selezionato in lista_orari:
                        conn.close()
                        flash('Locale già occupato per il giorno e la data selezionati. Scegliere un altro orario o giorno.', 'error')
                        return redirect(url_for('crea_corso'))
                
                    s = text("INSERT INTO corsi (titolo, descrizione, idlocale, datainizio, datafine, giorno, orarioinizio, cf) VALUES(:titolo, :descrizione, :idlocale, :datainizio, :datafine, :giorno, :orarioinizio, :cf)")
                    conn.execute(s, titolo = titolo, descrizione = descrizione, idlocale = idlocale, datainizio = datainizio, datafine = datafine, giorno = giorno, orarioinizio = orarioinizio, cf = current_user.get_id())
                    conn.execute("COMMIT")
                    conn.close()
                    return redirect(url_for('area_riservata'))
                except:
                    conn.execute("ROLLBACK")
                    conn.close()
                    flash('Non è stato possibile trovare i locali', 'error')
                    return redirect(url_for('area_riservata'))
                
            return render_template(
                'crea_corso.html',
                is_logged = is_logged(),
                title = 'Crea corso',
                year = datetime.now().year,
                message = 'Crea corso',
                form = form
            )
        except:
            conn.close()
            flash('Non è stato possibile trovare i locali', 'error')
            return redirect(url_for('area_riservata'))
    else:
        return redirect(url_for('home'))

"""
La funzione permette di creare nuovi locali inserendo metri quadri e il numero massimo di persone
"""
@app.route('/crea_locale', methods = ['GET', 'POST'])
@login_required
def crea_locale():
    if (current_user.get_tipo() == 'Gestore'):
        form = LocaliForm()
        if form.is_submitted():
            result = request.form
            try:
                mq = result['mq']
                personemax = result['personeMax']
                conn = engine.connect()
                s = text("INSERT INTO locali (mq, personemax, idpalestra) VALUES(:mq, :personemax, :idpalestra)")
                conn.execute(s, mq = mq, personemax = personemax, idpalestra = current_user.get_palestra())
                conn.close()
                return redirect(url_for('area_riservata'))
            except:
                conn.close()
                flash('Non è stato possibile trovare i locali', 'error')
                return redirect(url_for('area_riservata'))
        return render_template(
            'crea_locale.html',
            is_logged = is_logged(),
            title = 'Crea locale',
            year = datetime.now().year,
            message = 'Aggiungi un nuovo locale',
            form = form
        )
    else:
        return redirect(url_for('home'))

"""
Se si è positivi non ci si può prenotare.
Tramite le query si ottengono i corsi attualmente in svolgimento con possibilità di prenotazione.
"""
@app.route('/prenotazioni', methods = ['GET', 'POST'])
def prenotazioni():
    if (current_user.get_tipo() == 'Cliente'):
        if(current_user.get_tampone() == 'Positivo'):
            flash('Sei positivo, non puoi prenotarti','error')
            return redirect(url_for('area_riservata'))
        try:
            conn = engine.connect()
            s = text("SELECT c.idcorso, c.titolo FROM corsi c JOIN iscrizioni i USING (idcorso) WHERE i.cf =:cf AND c.sospeso = 'ATTIVO' ")
            corsi = conn.execute(s, cf = current_user.get_id())
            conn.close()

            lista_corsi = []
            for c in corsi:
                t = str(c['idcorso']) + ' - ' + str(c['titolo'])
                lista_corsi.append(t)

            form = BookingForm(lista_corsi)

            if form.is_submitted():
                result = request.form
                corso = result['corso'].split(' ')
                idcorso = corso[0]

                if result.get("ChooseDate", False):
                    conn = engine.connect()

                    s = text("SELECT c.datainizio, c.datafine, c.giorno FROM corsi c WHERE c.idcorso =:idcorso ")
                    dati_corso = conn.execute(s, idcorso = idcorso).fetchone()

                    s = text("SELECT p.data, l.personemax, COUNT(*) AS numeropersone FROM locali l NATURAL JOIN corsi c JOIN prenotazioni p USING(idcorso) WHERE c.idcorso =:idcorso GROUP BY p.data HAVING numeropersone >= l.personemax")
                    date_altri = conn.execute(s, idcorso = idcorso)
                    s = text("SELECT p.data FROM corsi c JOIN prenotazioni p USING(idcorso) WHERE c.idcorso =:idcorso AND p.cf =:cf")
                    date_mie = conn.execute(s, idcorso = idcorso, cf = current_user.get_id())
                    conn.close()

                    datainizio = dati_corso['datainizio']
                    datafine = dati_corso['datafine']
                    giorno = dati_corso['giorno']

                    lista = []
                    for l in date_altri:
                        lista.append(str(l['data']))
                    for l in date_mie:
                        lista.append(str(l['data']))

                    date = date_disponibili(str(datainizio), str(datafine), str(giorno))

                    date = date_rimanenti(date, lista)
                    
                    if len(date) == 0:
                        flash('Tutte le date sono già prenotate, scegliere un altro corso','error')
                        return redirect(url_for('prenotazioni'))

                    form.data.choices = date

                else:
                    data = result['data']

                    conn = engine.connect()
                    conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
                    conn.execute("START TRANSACTION")
                    s = text("INSERT INTO prenotazioni (cf, idcorso, data) VALUES(:cf, :idcorso, :data)")
                    conn.execute(s, cf = current_user.get_id(), idcorso = idcorso, data = data)
                    conn.close()

            return render_template(
                'prenotazioni.html',
                is_logged = is_logged(),
                title = 'Dettagli palestra',
                year = datetime.now().year,
                message = 'Prenotazioni',
                form = form
            )
        except:
            conn.close()
            flash('Non è stato possibile trovare i corsi', 'error')
            return redirect(url_for('area_riservata'))
    
    return redirect(url_for('home'))

"""
La funzione permette di visionare le prenotazioni e di cancellarle tramite dei Button accurati.
"""
@app.route('/mie_prenotazioni', methods = ['GET', 'POST'])
@login_required
def mie_prenotazioni():
    if (current_user.get_tipo() == 'Cliente'):
        form = DeleteBookingForm()
        try:
            conn = engine.connect()
            conn.execute("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")
            conn.execute("START TRANSACTION")
            if form.is_submitted():
                result = request.form
                idprenotazione = result['idprenotazione']
                s = text("DELETE FROM prenotazioni WHERE idprenotazione =:idprenotazione")
                conn.execute(s, idprenotazione = idprenotazione)
                conn.execute("COMMIT")
                conn.close()
                return redirect(url_for('mie_prenotazioni'))
            
            s = text("SELECT c.Titolo, p.Idprenotazione, p.Data, c.Orarioinizio FROM corsi c JOIN prenotazioni p USING(idcorso) WHERE p.CF =:cf AND p.data >= CURDATE()")
            prenotazioni = conn.execute(s, cf = current_user.get_id())
            lista_prenotazioni = []
            for p in prenotazioni:
                lista_prenotazioni.append(p)
            conn.close()
            return render_template(
                'mie_prenotazioni.html',
                is_logged = is_logged(),
                title = 'Mie prenotazioni',
                year = datetime.now().year,
                message = 'Ecco le tue prenotazioni',
                prenotazioni = lista_prenotazioni,
                form = form
            )
        except:
            conn.close()
            flash('Errore durante la richiesta dei dati dei corsi','error')
            return redirect(url_for('area_riservata'))
    return redirect(url_for('home'))