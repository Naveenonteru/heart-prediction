from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    predictions = db.relationship('Prediction', backref='user', lazy=True)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(1), nullable=False)
    cp = db.Column(db.String(1), nullable=False)  # chest pain type
    trestbps = db.Column(db.Integer, nullable=False)  # resting blood pressure
    chol = db.Column(db.Integer, nullable=False)  # serum cholesterol
    fbs = db.Column(db.String(1), nullable=False)  # fasting blood sugar
    restecg = db.Column(db.String(1), nullable=False)  # resting electrocardiographic results
    thalach = db.Column(db.Integer, nullable=False)  # maximum heart rate achieved
    exang = db.Column(db.String(1), nullable=False)  # exercise induced angina
    oldpeak = db.Column(db.Float, nullable=False)  # ST depression induced by exercise
    prediction_result = db.Column(db.Integer, nullable=False)  # 0 or 1
    probability = db.Column(db.Float, nullable=False)  # probability of heart disease
    risk_level = db.Column(db.String(20), nullable=False)  # Low, Moderate, High, Very High
    created_at = db.Column(db.DateTime, default=datetime.utcnow)