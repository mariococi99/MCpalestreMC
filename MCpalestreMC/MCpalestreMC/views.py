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
    def __init__ (self, cf, nome, cognome, email, utente, pwd, ruolo):
        self.cf = cf
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.utente = utente
        self.pwd = pwd
        self.ruolo = ruolo

    def get_ruolo(self):
        return self.ruolo

    def get_id(self):
        return self.id

def is_logged():
    return current_user.is_authenticated
"""
Funzione che serve per il corretto funzionamento dell'autenticazione.
"""
@login_manager.user_loader
def load_user (user_cf):
    conn = engine.connect()
    s = text("SELECT * FROM utenti WHERE CF =:utente")
    rs = conn.execute(s, utente=user_cf)
    user = rs.fetchone()
    conn.close()
    return User(user.CF, user.Nome, user.Cognome, user.Email, user.Password, user.Ruolo)

@app.route('/', methods = ['GET', 'POST'])
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title ='Home Page',
        year = datetime.now().year,
    )

@app.route('/contact', methods = ['GET', 'POST'])
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title = 'Contact',
        year = datetime.now().year,
        message = 'Your contact page.'
    )

@app.route('/about', methods = ['GET', 'POST'])
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.is_submitted():
        result = request.form
        try:
            cf = result['cf']
            password = result['password']
            conn = engine.connect()
            t = text('SELECT * FROM users u WHERE u.Cf =:cf AND u.Password =: password')
            u = conn.execute(t, cf = cf, password = password).fetch_one()
            conn.close()
            if u:
                flash("Errore durante l'accesso d", "error")
                return redirect(url_for("login"))
            else:
                user = User(u['Cf'], u['Email'], u['Nome'], u['Cognome'], u["Numero telefonico"], u['Password'], u['Ruolo'])
                login_user(user)
                engine = create_engine("mysql://" + utente + ":" + password + "@localhost/mcpalestremc")
                return redirect(url_for('area_riservata'))
        except:
            flash("Errore durante l'accesso", 'error')
            return redirect(url_for('login'))
    return render_template(
        "login.html",
        logged = current_user.is_authenticated,
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
            email = result['email']
            nome = result['nome']
            cognome = result['cognome']
            numero = result['telefono']
            password = result['password']
            conn = engine.connect()
            conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            conn.execute("START TRANSACTION")
            
            s = text("SELECT u.CF FROM users u WHERE u.CF =:cf") 
            id = conn.execute (s, cf = cf).fetchone()

            if id:
                conn.execute("COMMIT")
                conn.close()
                flash('Errore: inserire un codice fiscale diverso','error')
                return redirect(url_for('registrazione'))

            s = text("INSERT INTO users VALUES(:cf, :email, :nome, :cognome, :numero, :password, 'Utente')")
            rs = conn.execute (s, cf = cf, email = email, nome = nome, cognome = cognome, numero = numero, password = password)

            s=text("create user :codice@'localhost' identified with mysql_native_password by :password")
            rs = conn.execute (s, codice = cf, password = password)

            s=text("GRANT Cliente to :codice@'localhost'") 
            rs = conn.execute (s, codice = cf)

            rs = conn.execute ("FLUSH PRIVILEGES") 
            conn.execute("COMMIT")
            conn.close() 
            return redirect(url_for('loginPagina')) 
        except:
            conn.execute("ROLLBACK")
            conn.close()
            flash("Errore durante la registrazione", 'error')
            return redirect(url_for('registrazionePagina'))
    return render_template(
        "registrazione.html",
        logged = current_user.is_authenticated,
        title = 'Registrazione',
        year=datetime.now().year,
        form=form
        )