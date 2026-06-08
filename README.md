# 📈 Stock Price Prediction Web Application

A full-stack web application that leverages machine learning to forecast future stock prices. Built with a **Flask** backend and an interactive **HTML/CSS/JavaScript** frontend, this application fetches financial market data, processes historical trends, and visualizes price predictions.

---

## 🚀 Features

* **Authentication System:** Secure user registration (`register.html`) and login (`login.html`) functionality to manage personalized access.
* **Interactive Dashboard:** A comprehensive dashboard interface (`dahboard.html`) to visualize stock metrics and market trends.
* **Predictive Modeling:** Built-in predictive pipeline leveraging a trained machine learning model (`stock.pkl`) to forecast stock metrics via `predict.html`.
* **Real-Time Data Integration:** Secure configuration to handle external API integrations safely using dedicated environment keys.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3, JavaScript (ES6+), Chart.js / Plotly (for rendering interactive stock trends)
* **Backend:** Python 3.x, Flask
* **Machine Learning & Data Processing:** Scikit-Learn, Pandas, NumPy

---

## 📂 Project Structure

```text
├── templates/
│   ├── home.html               # Landing and welcome page
│   ├── register.html           # User account registration form
│   ├── login.html              # User authentication login form
│   ├── dahboard.html           # Main financial visualization dashboard
│   └── predict.html            # Prediction inputs and forecasting results
├── app.py                      # Flask application entry point & routing configuration
├── key.py                      # Secret key configurations and API authorization setups
├── ml_model.py                 # Machine learning data pipeline and inference logic
├── stock.pkl                   # Serialized pre-trained machine learning model artifact
└── stock prediction.ipynb      # Jupyter Notebook containing EDA and model training steps