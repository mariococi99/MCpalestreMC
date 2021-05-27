"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, url_for, request, flash, session, redirect
from flask_bootstrap import Bootstrap
from MCpalestreMC import app
from MCpalestreMC.forms import LoginForm
import sqlalchemy
from sqlalchemy import *
import flask_login
from flask_login import LoginManager, login_required, login_user, UserMixin, login_manager, logout_user, current_user

app.config['SECRET_KEY'] ='bgit4y5394rjfienvtn8'
login_manager = LoginManager()
login_manager.init_app(app)

uri = 'mysql://anonimo:anonimo@localhost/mcpalestremc' #collegamento al dbms
engine = create_engine(uri)
conn=engine.connect()
conn.execute("set global activate_all_roles_on_login = on") #attivazione ruoli
conn.close()

class User (UserMixin):
    def __init__ (self, cf, nome, cognome, email, pwd, ruolo):
        self.cf = cf
        self.email = email
        self.pwd = pwd
        self.nome = nome
        self.cognome = cognome
        self.ruolo = ruolo

    def get_ruolo(self):
        return self.ruolo

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user (user_cf):
    conn = engine.connect()
    s= text("SELECT * FROM utenti WHERE CF =:utente")
    rs = conn.execute(s, utente=user_cf)
    user = rs.fetchone()
    conn.close()
    return User(user.CF, user.Nome, user.Cognome, user.Email, user.Password, user.Ruolo)


def is_logged():
    return 'true' 

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        is_logged = is_logged(),
        message='Your application description page.'
    )

@app.route('/loginPagina', methods=['GET', 'POST'])
def loginPagina():
    return render_template("login.html", logged=current_user.is_authenticated) 

@app.route('/login', methods=['GET', 'POST'])
def login():
    global engine
    if request.method == 'POST':
        conn = engine.connect()
        s=text('SELECT * FROM users u WHERE u.ID =:id')
        rs = conn.execute (s, id=request.form['ID']).fetchone()
        if rs:
            real_pwd = rs['Password'] 
            conn.close()
            if(request.form['password']==real_pwd):
                user = User(rs['ID'],rs['Nome'],rs['Email'],rs['Password'],rs['Ruolo'])
                login_user(user)
                engine=create_engine("mysql://"+rs['ID']+":"+rs['Password']+"@localhost/compagniaaereamm")
                return redirect(url_for('areaRiservata'))
            else:
                flash('Errore: ID o password errati','error')
                return redirect(url_for('loginPagina'))
        else:
            flash('Errore: ID errato o non esistente','error')
            conn.close()
            return redirect(url_for('loginPagina'))
    else:
        return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.is_submitted():
        result = request.form
        try:
            utente = result['utente']
            password = result['password']
            return redirect(url_for('area_riservata'))
        except:
            reset_user()
            flash("Errore durante l'accesso", 'error')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    global engine
    engine = create_engine('mysql://anonimo:anonimo@localhost/compagniaaereamm')
    logout_user()
    return redirect(url_for('home')) 

@app.route('/registrazionePagina', methods=['GET', 'POST'])
def registrazionePagina():
    return render_template("registrazione.html", logged=current_user.is_authenticated) #render della pagina html "registrazione"

@app.route('/registrazione', methods=['GET', 'POST'])
def registrazione():
    conn=engine.connect()
    conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    conn.execute("START TRANSACTION")
    try:
        s=text("SELECT u.ID FROM users u WHERE u.ID =:codice") 
        id = conn.execute (s, codice=request.form['codice']).fetchone()

        if id:
            conn.execute("COMMIT")
            conn.close()
            flash('Errore: inserire un ID diverso','error')
            return redirect(url_for('registrazionePagina'))

        s=text("INSERT INTO users VALUES(:codice,:nome,:email,:password,'Cliente')")
        rs = conn.execute (s, codice=request.form['codice'],nome=request.form['utente'],email=request.form['inputEmail'],password=request.form['password'])

        s=text("create user :codice@'localhost' identified with mysql_native_password by :password")
        rs = conn.execute (s, codice=request.form['codice'],password=request.form['password'])

        s=text("GRANT Cliente to :codice@'localhost'") 
        rs = conn.execute (s, codice=request.form['codice'])

        rs = conn.execute ("FLUSH PRIVILEGES") 
        conn.execute("COMMIT")
        conn.close() 
        return redirect(url_for('loginPagina')) 
    except: 
        conn.execute("ROLLBACK")
        conn.close()
        flash('Errore: registrazione non riuscita, riprovare','error')
        return redirect(url_for('registrazionePagina')) 