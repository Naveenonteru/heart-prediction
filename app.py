import os
import logging
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import numpy as np
from utils.prediction_model import predict_heart_disease
from forms import LoginForm, RegisterForm, PredictionForm
from models import db, User, Prediction

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///heart_health.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# Authentication helper functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    user = User.query.get(session['user_id'])
    return render_template('home.html', user=user)

@app.route('/prediction', methods=['GET', 'POST'])
@login_required
def prediction():
    form = PredictionForm()
    result = None
    risk_level = None
    
    if form.validate_on_submit():
        # Collect form data
        features = [
            form.age.data,
            1 if form.sex.data == '1' else 0,  # 1 for male, 0 for female
            int(form.cp.data),
            form.trestbps.data,
            form.chol.data,
            1 if form.fbs.data == '1' else 0,
            int(form.restecg.data),
            form.thalach.data,
            1 if form.exang.data == '1' else 0,
            form.oldpeak.data,
            # Adding zeros for other features that our model might expect but are not in the form
            0, 0, 0  # Slope, CA, Thal (if needed)
        ]
        
        # Make prediction
        prediction_value, probability = predict_heart_disease(features)
        
        # Determine risk level
        if probability < 0.25:
            risk_level = "Low Risk"
        elif probability < 0.50:
            risk_level = "Moderate Risk"
        elif probability < 0.75:
            risk_level = "High Risk"
        else:
            risk_level = "Very High Risk"
        
        result = {
            'prediction': 'Positive' if prediction_value == 1 else 'Negative',
            'probability': round(probability * 100, 2),
            'risk_level': risk_level
        }
        
        # Save prediction to database
        user_id = session['user_id']
        new_prediction = Prediction(
            user_id=user_id,
            age=form.age.data,
            sex=form.sex.data,
            cp=form.cp.data,
            trestbps=form.trestbps.data,
            chol=form.chol.data,
            fbs=form.fbs.data,
            restecg=form.restecg.data,
            thalach=form.thalach.data,
            exang=form.exang.data,
            oldpeak=form.oldpeak.data,
            prediction_result=prediction_value,
            probability=probability,
            risk_level=risk_level
        )
        
        db.session.add(new_prediction)
        db.session.commit()
    
    # Get user's previous predictions
    user_predictions = Prediction.query.filter_by(user_id=session['user_id']).order_by(Prediction.created_at.desc()).limit(5).all()
    
    return render_template('prediction.html', form=form, result=result, risk_level=risk_level, 
                          predictions=user_predictions)

@app.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    try:
        data = request.get_json()
        
        # Collect data from request
        features = [
            data.get('age', 0),
            1 if data.get('sex', '0') == '1' else 0,
            int(data.get('cp', 0)),
            data.get('trestbps', 0),
            data.get('chol', 0),
            1 if data.get('fbs', '0') == '1' else 0,
            int(data.get('restecg', 0)),
            data.get('thalach', 0),
            1 if data.get('exang', '0') == '1' else 0,
            float(data.get('oldpeak', 0.0)),
            0, 0, 0  # Placeholder for other features if needed
        ]
        
        # Make prediction
        prediction_value, probability = predict_heart_disease(features)
        
        # Determine risk level
        if probability < 0.25:
            risk_level = "Low Risk"
        elif probability < 0.50:
            risk_level = "Moderate Risk"
        elif probability < 0.75:
            risk_level = "High Risk"
        else:
            risk_level = "Very High Risk"
        
        # Save prediction to database (optional for API calls)
        user_id = session['user_id']
        new_prediction = Prediction(
            user_id=user_id,
            age=data.get('age', 0),
            sex=data.get('sex', '0'),
            cp=data.get('cp', '0'),
            trestbps=data.get('trestbps', 0),
            chol=data.get('chol', 0),
            fbs=data.get('fbs', '0'),
            restecg=data.get('restecg', '0'),
            thalach=data.get('thalach', 0),
            exang=data.get('exang', '0'),
            oldpeak=float(data.get('oldpeak', 0.0)),
            prediction_result=prediction_value,
            probability=probability,
            risk_level=risk_level
        )
        
        db.session.add(new_prediction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'prediction': 'Positive' if prediction_value == 1 else 'Negative',
            'probability': round(probability * 100, 2),
            'risk_level': risk_level
        })
    
    except Exception as e:
        logging.error(f"Error in prediction API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# Help chatbot endpoint
@app.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    responses = {
        'symptoms': 'Common symptoms of heart disease include chest pain, shortness of breath, fatigue, irregular heartbeat, and dizziness.',
        'risk factors': 'Risk factors for heart disease include high blood pressure, high cholesterol, smoking, diabetes, obesity, poor diet, and lack of exercise.',
        'prevention': 'To prevent heart disease: maintain a healthy diet, exercise regularly, avoid smoking, limit alcohol, manage stress, and get regular checkups.',
        'treatment': 'Heart disease treatments may include lifestyle changes, medications, medical procedures like angioplasty, or surgery like bypass.',
        'help': 'You can ask me about heart disease symptoms, risk factors, prevention methods, or treatment options. How can I assist you?',
        'test': 'You can take a heart disease risk assessment by filling out the prediction form with your health data like blood pressure, cholesterol levels, and other indicators.'
    }
    
    response = "I'm sorry, I don't understand that question. You can ask me about heart disease symptoms, risk factors, prevention, or treatment."
    
    for key, value in responses.items():
        if key in message:
            response = value
            break
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)