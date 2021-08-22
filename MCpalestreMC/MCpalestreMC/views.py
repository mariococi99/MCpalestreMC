"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, url_for, request, flash, session, redirect
from flask_bootstrap import Bootstrap
from MCpalestreMC import app
from MCpalestreMC.forms import LoginForm, RegistrationForm
import sqlalchemy
from sqlalchemy import *
import flask_login
from flask_login import LoginManager, login_required, login_user, UserMixin, login_manager, logout_user, current_user

app.config['SECRET_KEY'] ='bgit4y5394rjfienvtn8'
login_manager = LoginManager()
login_manager.init_app(app)
bootstrap = Bootstrap(app)

uri = 'mysql://anonimo:anonimo@localhost/mcpalestremc' #collegamento al dbms
engine = create_engine(uri)
conn = engine.connect()
conn.execute("set global activate_all_roles_on_login = on") #attivazione ruoli
conn.close()

today = datetime.today().strftime('%Y-%m-%d')

class User (UserMixin):
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

    def get_ruolo(self):
        return self.ruolo

    def get_id(self):
        return self.cf

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

@app.route('/', methods = ['GET', 'POST'])
@app.route('/home', methods = ['GET', 'POST'])
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        is_logged = is_logged(),
        title ='Home Page',
        year = datetime.now().year,
    )

@app.route('/contact', methods = ['GET', 'POST'])
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        is_logged = is_logged(),
        title = 'Contact',
        year = datetime.now().year,
        message = 'Your contact page.'
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
                return redirect(url_for('home'))
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

@app.route('/area_riservata', methods=['GET', 'POST'])
@login_required
def area_riservata():
    return redirect(url_for('about')) 