from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from ml_model import predictor

app = Flask(__name__)
app.secret_key = '10eca762be55fdc99570c668bfad9d5a99700265713c2d492cd6ef3674d9ab68'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'users'  

# FIX 1: Force MySQL to return rows as dictionaries instead of raw tuples.
# This makes user['password'] work flawlessly regardless of column order!
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

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
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE User_name = %s', (user_name,))
        if cur.fetchone():
            flash('Username already exists!', 'danger')
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

# FIX 2: Upgraded Login Route using explicitly safe key mappings
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
        
        # Now accessing elements via actual dictionary column names
        if user and check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['User_name']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect Username or Password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Safer implementation: wipes all old trace parameters cleanly
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'loggedin' not in session:
        flash('Please log in to access this page', 'warning')
        return redirect(url_for('login'))
    
    prediction_result = None
    
    if request.method == 'POST':
        try:
            features = [
                float(request.form['open']),
                float(request.form['high']),
                float(request.form['low']),
                float(request.form['close']),
                float(request.form['adj_close']),
                float(request.form['returns']),
                int(request.form['year']),
                int(request.form['month']),
                int(request.form['quarter']),
                int(request.form['day'])
            ]
            
            predicted_price = predictor.predict(features)
            prediction_result = f"${predicted_price:,.2f}"
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('predict.html', 
                           username=session['username'],
                           prediction_result=prediction_result)

@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        flash('Please log in to access this page', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)