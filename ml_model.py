import joblib
import numpy as np
import os

class StockPredictor:
    def __init__(self, model_path='stock.pkl'):
        self.model = None
        self.model_path = model_path
        self.load_model()
    
    def load_model(self):
        """Load your regression stock.pkl model"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print(f"✅ Your stock.pkl model loaded successfully!")
                print(f"Model type: {type(self.model).__name__}")
                if hasattr(self.model, 'n_features_in_'):
                    print(f"Expected features: {self.model.n_features_in_} (matches your 10 input features)")
            except Exception as e:
                print(f"❌ Error loading stock.pkl: {e}")
                self.model = None
        else:
            print(f"❌ stock.pkl not found at {os.path.abspath(self.model_path)}")
            self.model = None
    
    def predict(self, features):
        """Predict using your features array and return a numeric stock price"""
        if self.model is None:
            raise Exception("stock.pkl model not loaded. Place stock.pkl in the same folder as app.py")
        
        try:
            # Reshape features to a 2D array (1 sample, 10 features)
            features_array = np.array(features).reshape(1, -1)
            
            # For regression, this extracts the continuous target value (the target price)
            predicted_price = self.model.predict(features_array)[0]
            
            # Return the value as a basic float
            return float(predicted_price)
            
        except Exception as e:
            raise Exception(f"Prediction error: {str(e)}")

# Global instance for your model
predictor = StockPredictor('stock.pkl')