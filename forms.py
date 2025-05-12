from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, EqualTo, NumberRange, ValidationError

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

class PredictionForm(FlaskForm):
    age = IntegerField('Age', validators=[
        DataRequired(),
        NumberRange(min=18, max=100, message='Age must be between 18 and 100.')
    ])
    
    sex = SelectField('Sex', choices=[
        ('', 'Select'),
        ('1', 'Male'),
        ('0', 'Female')
    ], validators=[DataRequired()])
    
    cp = SelectField('Chest Pain Type', choices=[
        ('', 'Select'),
        ('1', 'Typical Angina'),
        ('2', 'Atypical Angina'),
        ('3', 'Non-anginal Pain'),
        ('4', 'Asymptomatic')
    ], validators=[DataRequired()])
    
    trestbps = IntegerField('Resting Blood Pressure (mm Hg)', validators=[
        DataRequired(),
        NumberRange(min=80, max=200, message='Blood pressure must be between 80 and 200.')
    ])
    
    chol = IntegerField('Serum Cholesterol (mg/dl)', validators=[
        DataRequired(),
        NumberRange(min=100, max=600, message='Cholesterol must be between 100 and 600.')
    ])
    
    fbs = SelectField('Fasting Blood Sugar > 120 mg/dl', choices=[
        ('', 'Select'),
        ('1', 'Yes'),
        ('0', 'No')
    ], validators=[DataRequired()])
    
    restecg = SelectField('Resting ECG Results', choices=[
        ('', 'Select'),
        ('0', 'Normal'),
        ('1', 'ST-T Wave Abnormality'),
        ('2', 'Left Ventricular Hypertrophy')
    ], validators=[DataRequired()])
    
    thalach = IntegerField('Maximum Heart Rate Achieved', validators=[
        DataRequired(),
        NumberRange(min=60, max=220, message='Heart rate must be between 60 and 220.')
    ])
    
    exang = SelectField('Exercise Induced Angina', choices=[
        ('', 'Select'),
        ('1', 'Yes'),
        ('0', 'No')
    ], validators=[DataRequired()])
    
    oldpeak = FloatField('ST Depression Induced by Exercise', validators=[
        DataRequired(),
        NumberRange(min=0, max=10, message='ST depression must be between 0 and 10.')
    ])
    
    submit = SubmitField('Predict Risk')