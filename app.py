import warnings
from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
from ml_model import predictor  # Utilize the central model wrapper

# ------------------------------------------------------------------
# 1. Suppress Scikit-Learn Warnings
# ------------------------------------------------------------------
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# ------------------------------------------------------------------
# 2. Initialize Flask App
# ------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "super_secret_stock_app_key"

# Mock Database
users_db = {"demo": "password123"}




# ------------------------------------------------------------------
# 3. App Routes
# ------------------------------------------------------------------
@app.route('/')
def home():
    print(">>> SERVING HOME PAGE <<<")
    # Show home landing page regardless of session
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users_db and users_db[username] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        flash("Invalid username or password.", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users_db:
            flash("User already exists.", "danger")
        else:
            users_db[username] = password
            flash("Account created! Please log in.", "success")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))

    prediction_result = None
    form_data = {}

    if request.method == 'POST':
        form_data = request.form.to_dict()
        try:
            # Map input fields to exact DataFrame column names expected by stock.pkl
            feature_dict = {
                'Open': float(request.form['open']),
                'High': float(request.form['high']),
                'Low': float(request.form['low']),
                'Close': float(request.form['close']),
                'Adj Close': float(request.form['adj_close']),
                'Returns': float(request.form['returns']),
                'Year': int(request.form['year']),
                'Month': int(request.form['month']),
                'Quarter': int(request.form['quarter']),
                'Day': int(request.form['day'])
            }

            # Convert dictionary into a Pandas DataFrame with exact column headers
            input_df = pd.DataFrame([feature_dict])

            # Pass DataFrame directly to the predictor
            predicted_val = predictor.predict(input_df)
            
            # If predictor returns an array or series, extract scalar float
            if hasattr(predicted_val, '__len__'):
                predicted_val = predicted_val[0]

            prediction_result = f"${float(predicted_val):,.2f}"

        except KeyError as ke:
            flash(f"Missing required input field: {str(ke)}", "danger")
        except ValueError:
            flash("Please enter valid numerical values in all fields.", "danger")
        except Exception as e:
            flash(f"Prediction error: {str(e)}", "danger")

    return render_template(
        'predict.html', 
        prediction_result=prediction_result, 
        form_data=form_data, 
        username=session.get('username')
    )

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)