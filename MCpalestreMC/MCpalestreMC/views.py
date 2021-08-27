"""
Questi import servono per far funzionare interamente l'applicazione web
"""
from datetime import datetime
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
bootstrap = Bootstrap(app) #Istanziamento della classe Bootstrap per

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
Questa funzione serve per vedere se l'utente è loggato o meno
Visto che il passaggio di dati da javascript a python può sollevare problemi,
si è preferito scrivere una funzione per risolvere la questione
"""
def is_logged():
    if current_user.is_authenticated:
        return 'true'
    return 'false'

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
La funzione home ritorna il rendering della pagina principale/iniziale
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

@app.route('/about', methods = ['GET', 'POST'])
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        is_logged = is_logged(),
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    global engine
    form = LoginForm()
    if form.is_submitted():
        result = request.form
        try:
            cf = result['cf']
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
        year=datetime.now().year,
        form=form
        ) 

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    global engine
    engine = create_engine('mysql://anonimo:anonimo@localhost/mcpalestremc')
    logout_user()
    return redirect(url_for('home')) 

@app.route('/registrazione', methods=['GET', 'POST'])
def registrazione():
    form = RegistrationForm()
    if form.is_submitted():
        result = request.form
        try:
            cf = result['cf']
            nome = result['nome']
            cognome = result['cognome']
            email = result['email']
            numero = result['numero']
            password = result['password']

            conn = engine.connect()

            conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            conn.execute("START TRANSACTION")
            
            s = text("SELECT u.CF FROM utenti u WHERE u.CF =:cf")
            id = conn.execute(s, cf = cf).fetchone()
            
            if id:
                conn.execute("COMMIT")
                conn.close()
                flash('Errore: codice fiscale già registrato','error')
                return redirect(url_for('registrazione'))

            s = text("INSERT INTO utenti VALUES(:cf, :nome, :cognome, :email, :numero, :password, 'Negativo', 'Cliente', '1')")
            rs = conn.execute (s, cf = cf, nome = nome, cognome = cognome, email = email, numero = numero, password = password)
            
            s = text("create user :codice@'localhost' identified with mysql_native_password by :password")
            rs = conn.execute (s, codice = cf, password = password)

            s = text("GRANT Cliente to :codice@'localhost'")
            rs = conn.execute(s, codice = cf)

            rs = conn.execute("FLUSH PRIVILEGES")
            conn.execute("COMMIT")
            conn.close() 
            return redirect(url_for('login')) 
        except:
            conn.execute("ROLLBACK")
            conn.close()
            flash("Errore durante la registrazione", 'error')
            return redirect(url_for('registrazione'))
    return render_template(
        "registrazione.html",
        is_logged = is_logged(),
        title = 'Registrazione',
        year=datetime.now().year,
        form=form
        )

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
                year=datetime.now().year,
                form = form
            )
        except:
            conn.execute("ROLLBACK")
            conn.close()
            flash("Errore durante la registrazione", 'error')
            return redirect(url_for('registra_istruttore'))
        
    return redirect(url_for('home'))

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

                    s = text("INSERT INTO palestre (titolo, indirizzo, email, telefono, cf) VALUES(:titolo, :indirizzo, :email, :telefono, :cf)")
                    rs = conn.execute (s, titolo = palestra, indirizzo = indirizzo, email = emailPalestra, telefono = telefono, cf = cf)

                    s = text("SELECT idpalestra FROM palestre WHERE CF =:cf")
                    idpalestra = conn.execute(s, cf = cf).fetchone()

                    for l in locali:
                        mq = l['mq'].data
                        personemax = l['personeMax'].data
                        s = text("INSERT INTO locali (mq, personemax, idpalestra) VALUES(:mq, :personemax, :idpalestra)")
                        rs = conn.execute (s, mq = mq, personemax = personemax, idpalestra = idpalestra)

                    s = text("INSERT INTO utenti VALUES(:cf, :nome, :cognome, :email, :numero, :password, 'Negativo', 'Gestore', :idpalestra)")
                    rs = conn.execute (s, cf = cf, nome = nome, cognome = cognome, email = email, numero = numero, password = password, palestra = idpalestra)
            
                    s = text("create user :codice@'localhost' identified with mysql_native_password by :password")
                    rs = conn.execute (s, codice = cf, password = password)

                    s = text("GRANT Gestore to :codice@'localhost'")
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

@app.route('/palestre', methods = ['GET'])
def palestre():
    lista_palestre = []
    try:
        conn = engine.connect()
        s = text("SELECT p.Titolo, p.Indirizzo, p.Email, p.Telefono, u.Nome, u.Cognome FROM palestre p JOIN utenti u USING (cf)")
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
        title='Palestre',
        year=datetime.now().year,
        message='Your application description page.',
        palestre = lista_palestre
    )

@app.route('/corsi', methods = ['GET'])
def corsi():
    lista_corsi = []
    try:
        conn = engine.connect()
        s = text("SELECT c.Idcorso, c.Titolo, u.Nome, u.Cognome c.Descrizione, c.Idlocale, c.Giorno, c.Orarioinizio, c.Datainizio, c.Datafine FROM corsi c NATURAL JOIN utenti u")
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
            title='Corsi',
            year=datetime.now().year,
            message='Your application description page.',
            corsi = lista_corsi
        )
    
@app.route('/abbonamenti', methods = ['GET'])
def abbonamenti():
    return render_template(
        'abbonamenti.html',
        is_logged = is_logged(),
        title='Abbonamenti',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/area_gestore', methods = ['GET'])
@login_required
def area_gestore():
    if (current_user.get_tipo() == 'Gestore'):
        try:
            conn = engine.connect()
            s=text("SELECT p.Titolo, p.Indirizzo, p.Email, p.Telefono, COUNT(u.tipo) AS Personeiscritte FROM palestre p LEFT JOIN utenti u USING (idpalestra) WHERE u.tipo = 'Cliente' AND p.idpalestra =:idpalestra ")
            palestra = conn.execute(s, idpalestra = current_user.get_palestra()).fetchone()
            conn.close()
            return render_template(
                'area_gestore.html',
                is_logged = is_logged(),
                title='Area riservata | Gestore',
                year=datetime.now().year,
                message='Your application description page.',
                palestra = palestra
            )
        except:
            conn.close()
            flash('Erroe durante la richiesta dei dati della palestra','error')
            return redirect(url_for('home'))
    return redirect(url_for('home'))
    

@app.route('/area_istruttore', methods = ['GET', 'POST'])
@login_required
def area_istruttore():
    if (current_user.get_tipo() == 'Istruttore'):
        form1 = CovidForm()
        form2 = SubscriptionForm()
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
            s=text("SELECT c.Idcorso, c.Titolo, c.Descrizione, c.Idlocale, c.Giorno, c.Orarioinizio, c.Datainizio, c.Datafine, COUNT(i.cf) AS Personeiscritte FROM corsi c LEFT JOIN iscrizioni i ON c.idcorso = i.idcorso WHERE c.CF =:cf GROUP BY c.idcorso")
            corsi = conn.execute(s, cf = current_user.get_id())
            lista_corsi = []
            for c in corsi:
                lista_corsi.append(c)
            conn.close()
            return render_template(
                'area_istruttore.html',
                is_logged = is_logged(),
                title='Area riservata | Istruttore',
                year=datetime.now().year,
                message='Your application description page.',
                corsi = lista_corsi,
                form1 = form1,
                form2 = form2
            )
        except:
            conn.close()
            flash('Errore durante la richiesta dei dati dei corsi','error')
            return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/area_cliente', methods = ['GET', 'POST'])
@login_required
def area_cliente():
    if (current_user.get_tipo() == 'Cliente'):
        form1 = CovidForm()
        form2 = SubscriptionForm()
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
            s=text("SELECT c.Idcorso, c.Titolo, u.Nome, u.Cognome, c.Descrizione, c.Idlocale, c.Giorno, c.Orarioinizio, c.Datainizio, c.Datafine FROM utenti u NATURAL JOIN corsi c JOIN iscrizioni i USING(idcorso) WHERE i.CF =:cf")
            corsi = conn.execute(s, cf = current_user.get_id())
            lista_corsi = []
            for c in corsi:
                lista_corsi.append(c)
            conn.close()
            return render_template(
                'area_cliente.html',
                is_logged = is_logged(),
                title='Area riservata | Cliente',
                year=datetime.now().year,
                message='Your application description page.',
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

@app.route ('/modifica_profilo', methods=['GET', 'POST'])
@login_required
def modifica_profilo():
    try:
        conn = engine.connect()
        conn.execute("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")
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
        title = 'Modifica profilo cliente',
        year = datetime.now().year,
        message = 'Il cliente desidera modificarsi',
        form = form
    )

@app.route('/altri_corsi', methods = ['GET', 'POST'])
@login_required
def altri_corsi():
    if (current_user.get_tipo() == 'Cliente'):
        form = SubscriptionForm()
        if form.is_submitted():
            try:
                result = request.form
                idcorso = result['idcorso']
                conn = engine.connect()
                conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
                conn.execute("START TRANSACTION")
                s = text("INSERT INTO iscrizioni VALUES (:idcorso, :cf)")
                conn.execute(s, idcorso = idcorso, cf = current_user.get_id())
                conn.execute("COMMIT")
                conn.close()
                return redirect(url_for('altri_corsi'))
            except:
                conn.close()
                flash('Qualcosa è andato storto', 'error')
                return redirect(url_for('area_riservata'))
        try:
            conn = engine.connect()
            s = text("SELECT c.Idcorso, c.Titolo, u.Nome, u.Cognome, c.Descrizione, c.Idlocale, c.Giorno, c.Orarioinizio, c.Datainizio, c.Datafine FROM corsi c NATURAL JOIN utenti u WHERE :cf NOT IN (SELECT i.CF FROM iscrizioni i WHERE i.idcorso = c.idcorso)")
            corsi = conn.execute(s, cf = current_user.get_id())
            conn.close()
            lista_corsi = []
            for c in corsi:
                lista_corsi.append(c)
            
            return render_template(
                'altri_corsi.html',
                is_logged = is_logged(),
                title = 'Altri corsi',
                year = datetime.now().year,
                message = 'Your application description page.',
                corsi = lista_corsi,
                form = form
            )
        except:
            conn.close()
            flash('Non è stato possibile trovare altri corsi', 'error')
            return redirect(url_for('area_riservata'))
    else:
        return redirect(url_for('home'))

@app.route('/crea_corso', methods = ['GET', 'POST'])
@login_required
def crea_corso():
    if (current_user.get_tipo() == 'Istruttore' or current_user.get_tipo() == 'Gestore'):
        try:
            conn = engine.connect()
            s = text("SELECT idlocale FROM locali WHERE idpalestra =:idpalestra")
            idlocali = conn.execute(s, idpalestra = current_user.get_palestra())
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
                #to change
                s = text("INSERT INTO corsi (titolo, descrizione, idlocale, cf) VALUES(:titolo, :descrizione, :idlocale, :cf)")
                conn.execute(s, titolo = titolo, descrizione = descrizione, idlocale = idlocale, cf = current_user.get_id())
                conn.close()
                flash('Nuovo corso aggiunto!')
                return redirect(url_for('area_riservata'))
            conn.close()    
            return render_template(
                'crea_corso.html',
                is_logged = is_logged(),
                title = 'Crea corso',
                year = datetime.now().year,
                message = 'Your application description page.',
                form = form
            )
        except:
            conn.close()
            flash('Non è stato possibile trovare i locali', 'error')
            return redirect(url_for('area_riservata'))
    else:
        return redirect(url_for('home'))

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
                flash('Nuovo locale aggiunto!')
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
            message = 'Your application description page.',
            form = form
        )
    else:
        return redirect(url_for('home'))


@app.route('/dettagli_palestra', methods = ['GET', 'POST'])
def dettagli_palestra():
    return render_template(
        'dettagli_palestra.html',
        is_logged = is_logged(),
        title='Dettagli palestra',
        year=datetime.now().year,
        message='Your application description page.'
    )