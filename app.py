from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from ml_model import predictor


app = Flask(__name__)
app.secret_key = '10eca762be55fdc99570c668bfad9d5a99700265713c2d492cd6ef3674d9ab68'

# MySQL configuration - UPDATE THESE 4 LINES
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'users'  # ← YOUR DB NAME FROM PHPMYADMIN

mysql = MySQL(app)

@app.route('/')
def home():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        
        # Check if user exists
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE User_name = %s', (user_name,))
        if cur.fetchone():
            flash('User_name already exists!', 'danger')
            cur.close()
            return render_template('register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        cur.execute('INSERT INTO user (User_name, password) VALUES (%s, %s)', 
                   (user_name, hashed_password))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# FIXED Login - Uses TUPLE INDEXING (user[2] = password column)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE User_name = %s', (username,))
        user = cur.fetchone()
        cur.close()
        
        # FIXED: user[0]=ID, user[1]=User_name, user[2]=password
        if user and check_password_hash(user[2], password):
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[1]
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect User_name/password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'loggedin' not in session:
        flash('Please log in to access this page', 'warning')
        return redirect(url_for('login'))
    
    prediction_result = None
    probability = None
    
    if request.method == 'POST':
        try:
            # YOUR 10 FEATURES (NO VOLUME)
            features = [
                float(request.form['open']),
                float(request.form['high']),
                float(request.form['low']),
                float(request.form['close']),
                float(request.form['adj_close']),  # ← Volume REMOVED
                float(request.form['returns']),
                int(request.form['year']),
                int(request.form['month']),
                int(request.form['quarter']),
                int(request.form['day'])
            ]
            
            prediction, prob = predictor.predict(features)
            
            # Handle prediction output
            if isinstance(prediction, (int, float)) and (prediction == 1 or prediction > 0.5):
                prediction_result = f"🟢 STOCK WILL GO UP (BUY) - {prediction}"
            else:
                prediction_result = f"🔴 STOCK WILL GO DOWN (SELL) - {prediction}"
            
            probability = prob
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('predict.html', 
                         username=session['username'],
                         prediction_result=prediction_result,
                         probability=probability)


@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        flash('Please log in to access this page', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)
