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
    palestra = SelectField('Palestra', [])
    registrationSubmit = SubmitField('Invia')

    def __init__(self, palestre = None, **kwargs):
       super().__init__(**kwargs)
       self['palestra'].choices = palestre

class InstructorRegistrationForm(FlaskForm):
    cf = StringField('Codice fiscale')
    nome = StringField('Nome')
    cognome = StringField('Cognome')
    email = EmailField('E-mail')
    numero = StringField('Numero telefonico')
    password = PasswordField('Password')
    palestra = SelectField('Palestra', [])
    instructorRegistrationSubmit = SubmitField('Invia')

    def __init__(self, palestre = None, **kwargs):
        super().__init__(**kwargs)
        self['palestra'].choices = palestre

class RoomForm(FlaskForm):
    mq = FloatField('Metri quadri locale')
    personeMax = DecimalField('Capienza massima persone')

class GymManagerRegistrationForm(FlaskForm):
    cf = StringField('Codice fiscale')
    nome = StringField('Nome')
    cognome = StringField('Cognome')
    email = EmailField('E-mail')
    numero = StringField('Numero telefonico')
    password = PasswordField('Password')
    palestra = StringField('Nome palestra')
    indirizzo = StringField('Indirizzo palestra')
    emailPalestra = EmailField('E-mail palestra')
    telefono = StringField('Numero telefonico palestra')
    locali = FieldList(FormField(RoomForm), min_entries=2)
    gymManagerRegistrationSubmit = SubmitField('Invia')

class LocaliForm(FlaskForm):
    mq = FloatField('Metri quadri locale')
    personeMax = DecimalField('Capienza massima persone')
    localiSubmit = SubmitField('Invia')

class ProfileModificationForm(FlaskForm):
    email = EmailField('E-mail')
    numero = StringField('Numero telefonico')
    idPalestra = SelectField('Palestra', [])
    profileModificationSubmit = SubmitField('Invia')

    def __init__(self, palestre = None, **kwargs):
        super().__init__(**kwargs)
        self['idPalestra'].choices = palestre

class CovidForm(FlaskForm):
    covid = BooleanField('Covid-19')
    covidSubmit = SubmitField('Segnala')

class CourseCreationForm(FlaskForm):
    titolo = StringField('Titolo')
    descrizione = TextAreaField('Aggiungi descrizione')
    dataInizio = DateField('Data di inizio corso')
    dataFine = DateField('Data di fine corso')
    giorno = SelectField('Giorno della settimana', choices = ['Luned??','Marted??','Mercoled??','Gioved??','Venerd??','Sabato','Domenica'])
    orarioInizio = SelectField('Orario', choices = ['08:00','10:00','12:00','14:00','16:00','18:00','20:00'])
    idLocale = SelectField('Locale', [])
    courseCreationSubmit = SubmitField('Invia')

    def __init__(self, locali = None, **kwargs):
        super().__init__(**kwargs)
        self['idLocale'].choices = locali

class SubscriptionForm(FlaskForm):
    subscriptionSubmit = SubmitField('Iscriviti')

class UnsubscriptionForm(FlaskForm):
    unsubscriptionSubmit = SubmitField('Disiscriviti')

class DeleteCourseForm(FlaskForm):
    deleteCourseSubmit = SubmitField('Cancella')

class BookingForm(FlaskForm):
    corso = SelectField('Corso', [])
    data = SelectField('Data prenotazione', [])
    bookingSubmit = SubmitField('Prenota')

    def __init__(self, corsi = None, date = None, **kwargs):
        super().__init__(**kwargs)
        self['corso'].choices = corsi
        self['data'].choices = date

class DeleteBookingForm(FlaskForm):
    deleteBookingSubmit = SubmitField('Cancellami')