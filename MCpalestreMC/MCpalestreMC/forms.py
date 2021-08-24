from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import EmailField

class LoginForm(FlaskForm):
    cf = StringField('Codice fiscale')
    password = PasswordField('Password')
    loginSubmit = SubmitField('Invia')

class RegistrationForm(FlaskForm):
    cf = StringField('Codice fiscale')
    nome = StringField('Nome')
    cognome = StringField('Cognome')
    email = EmailField('E-mail')
    numero = StringField('Numero telefonico')
    password = PasswordField('Password')
    registrationSubmit = SubmitField('Invia')

class ProfileModificationForm(FlaskForm):
    email = EmailField('E-mail')
    numero = StringField('Numero telefonico')
    idPalestra = StringField('Idpalestra')
    profileModificationSubmit = SubmitField('Invia')