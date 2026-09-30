import joblib
import pandas as pd
import numpy as np
import os

class StockPredictor:
    def __init__(self, model_path='stock.pkl'):
        self.model = None
        self.model_path = model_path
        # Match exact capitalization used when training stock.pkl
        self.feature_names = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Returns', 'Year', 'Month', 'Quarter', 'Day']
        self.load_model()
    
    def load_model(self):
        """Load the regression stock.pkl model"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print(f"✅ stock.pkl model loaded successfully!")
            except Exception as e:
                print(f"❌ Error loading stock.pkl: {e}")
                self.model = None
        else:
            print(f"⚠️ stock.pkl not found at {os.path.abspath(self.model_path)}.")
            self.model = None
    
    def predict(self, features):
        """Predict using the 10-feature list or array"""
        if self.model is None:
            raise Exception("Model file (stock.pkl) is missing or unreadable.")
        
        try:
            # If features is already a DataFrame, ensure columns match; otherwise build DataFrame
            if isinstance(features, pd.DataFrame):
                input_df = features[self.feature_names]
            else:
                input_df = pd.DataFrame([features], columns=self.feature_names)
                
            predicted_price = self.model.predict(input_df)[0]
            return float(predicted_price)
        except Exception as e:
            raise Exception(f"Prediction calculation error: {str(e)}")

predictor = StockPredictor('stock.pkl')