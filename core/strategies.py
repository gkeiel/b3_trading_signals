import json
import pandas as pd


# =====================================================
#  Strategy Manager
# =====================================================
class Strategies:
    def __init__(self, file_config="config.json"):
        self.load_config(file_config)

    def load_config(self, path):
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
            self.preset = config.get("preset", "basic")
            
    PRESET = {
        "basic":     {"w_return": 1.0, "w_trades": 0.02, "w_sharpe": 0,    "w_drdown": 0},
        "balanced":  {"w_return": 1.0, "w_trades": 0.04, "w_sharpe": 0.01, "w_drdown": 0.05},
        "agressive": {"w_return": 1.0, "w_trades": 0,    "w_sharpe": 0.02, "w_drdown": 0},
        "defensive": {"w_return": 1.0, "w_trades": 0.05, "w_sharpe": 0,    "w_drdown": 0.05},
    }
            
    def load_config(self, path):
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
            cfg    = config.get("backtest", {})
        self.preset = cfg.get("preset", "basic")
    
    def best_strategy(self, res_data, **weights):
        """
        Manages scoring presets for strategy in a deterministic grid evaluation:
        tests all parameter combinations and ranks them using
        weighted objective scores defined by each preset.
        """
        bst_data = {}

        params = {**self.PRESET[self.preset], **weights}
        w_return = params["w_return"]
        w_trades = params["w_trades"]
        w_sharpe = params["w_sharpe"]
        w_drdown = params["w_drdown"]
        
        
        for ticker, ticker_results in res_data.items():
            df = pd.DataFrame.from_dict(ticker_results, orient="index")
            
            # calculate SCORE (higher is better)
            df["Score"] = (
                w_return*df["Return_Strategy"]
                -w_trades*df["Trades"]
                +w_sharpe*df["Sharpe"]
                -w_drdown*df["Max_Drawdown"]
            )
            bst_data[ticker] = df.sort_values("Score", ascending=False)
        return bst_data
    
    def import_strategies(self, csv_file):
        # import strategies
        strategies = pd.read_csv(csv_file).set_index("Ticker").to_dict("index")
        return strategies