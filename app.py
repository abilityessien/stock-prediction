import warnings
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
import yfinance as yf
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

# Popular stock ticker shortcuts for quick UI selection
POPULAR_TICKERS = ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA"]


# ------------------------------------------------------------------
# 3. App Routes
# ------------------------------------------------------------------
@app.route('/')
def home():
    print(">>> SERVING HOME PAGE <<<")
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
    raw_prediction = None
    form_data = {}
    selected_ticker = ""

    # Check if user requested auto-fill via ticker lookup (URL query or form)
    ticker_param = request.args.get('ticker') or request.form.get('fetch_ticker')
    
    if ticker_param:
        selected_ticker = ticker_param.strip().upper()
        try:
            stock = yf.Ticker(selected_ticker)
            df = stock.history(period="5d")

            if df.empty:
                flash(f"Could not fetch data for ticker '{selected_ticker}'. Please check the symbol.", "danger")
            else:
                # Extract the latest market day row and date
                latest_row = df.iloc[-1]
                latest_date = df.index[-1]

                # Compute Daily Return based on previous day close
                prev_close = df['Close'].iloc[-2] if len(df) > 1 else latest_row['Open']
                daily_return = (latest_row['Close'] - prev_close) / prev_close

                # Populate form fields automatically
                form_data = {
                    'open': round(float(latest_row['Open']), 2),
                    'high': round(float(latest_row['High']), 2),
                    'low': round(float(latest_row['Low']), 2),
                    'close': round(float(latest_row['Close']), 2),
                    'adj_close': round(float(latest_row['Close']), 2),
                    'returns': round(float(daily_return), 4),
                    'year': int(latest_date.year),
                    'month': int(latest_date.month),
                    'quarter': int((latest_date.month - 1) // 3 + 1),
                    'day': int(latest_date.day)
                }
                flash(f"Successfully loaded live market data for {selected_ticker}!", "success")

        except Exception as e:
            flash(f"Failed to fetch market data: {str(e)}", "danger")

    # Handle prediction submission
    if request.method == 'POST' and ('calculate_prediction' in request.form or 'open' in request.form):
        # Merge form submission data so fields persist
        form_data.update(request.form.to_dict())
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

            # Convert dictionary into Pandas DataFrame
            input_df = pd.DataFrame([feature_dict])

            # Pass DataFrame directly to predictor
            predicted_val = predictor.predict(input_df)

            if hasattr(predicted_val, '__len__'):
                predicted_val = predicted_val[0]

            raw_prediction = float(predicted_val)
            prediction_result = f"₦{raw_prediction:,.2f}"

        except KeyError as ke:
            flash(f"Missing required input field: {str(ke)}", "danger")
        except ValueError:
            flash("Please enter valid numerical values in all fields.", "danger")
        except Exception as e:
            flash(f"Prediction error: {str(e)}", "danger")

    return render_template(
        'predict.html', 
        prediction_result=prediction_result,
        raw_prediction=raw_prediction,
        form_data=form_data, 
        selected_ticker=selected_ticker,
        popular_tickers=POPULAR_TICKERS,
        username=session.get('username')
    )

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)