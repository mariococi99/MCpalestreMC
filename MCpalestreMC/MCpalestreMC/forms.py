from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import EmailField

class LoginForm(FlaskForm):
    utente = StringField('Nome utente')
    password = PasswordField('Password')
    loginSubmit = SubmitField('Invia')

class RegistrationForm(FlaskForm):
    cf = StringField('Codice fiscale')
    email = StringField('Email')
    nome = StringField('Nome')
    cognome = StringField('Cognome')
    telefono = StringField('Numero telefonico')
    password = StringField('Password')
    registrationSubmit = SubmitField('Invia')