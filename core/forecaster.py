import json
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor


# =====================================================
#  Forecaster
# =====================================================
class Forecaster:
    def __init__(self, df, file_config="config.json"):
        self.df = df.copy()
        self.model  = None
        self.load_config(file_config)
        
    def load_config(self, path):
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
            cfg    = config.get("forecast", {})
            
        self.method = cfg.get("method", "RF")
        self.n_lags = cfg.get("lags", 5)
        self.n_estimators = cfg.get("n_estimators", 10)
        self.max_depth = cfg.get("max_depth", 5)
        
    def predictions(self):
        df = self.df
        y  = df["Close"]

        # build features for ML model
        X, Y = [], []
        for i in range(self.n_lags, len(y)):
            X.append(y.iloc[i-self.n_lags:i])
            Y.append(y.iloc[i])
        X = np.array(X)
        Y = np.array(Y)

        # train decision trees
        if self.method == "RF":
            model = RandomForestRegressor(n_estimators=self.n_estimators, max_depth=self.max_depth, random_state=0)
        elif self.method == "DT":
            model = DecisionTreeRegressor(max_depth=self.max_depth)
        model.fit(X, Y)
        self.model = model

        # predictions
        y_hat = model.predict(X)
        
        # add to dataframe
        df["Predicted_Close"] = np.nan
        df.loc[df.index[self.n_lags:], "Predicted_Close"] = y_hat
        return df
    
    def predict_next(self):
        if self.model is None:
            raise ValueError("No existing model.")
        last_Y = self.df["Close"].iloc[-self.n_lags:].values.reshape(1, -1)               
        y_hat  = self.model.predict(last_Y)[0]
        return y_hat