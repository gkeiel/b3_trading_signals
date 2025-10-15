import os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib 
import requests
from dotenv import load_dotenv
matplotlib.use("Agg")


# =====================================================
#  Loader
# =====================================================
class Loader:
    def __init__(self, file_tickers=None, file_indicators=None):
        self.file_tickers = file_tickers
        self.file_indicators = file_indicators

    def load_tickers(self):
        with open(self.file_tickers, "r", encoding="utf-8") as f:
            tickers = [line.strip() for line in f if line.strip()]
        return tickers
    
    def load_indicators(self):
        indicators = []
        with open(self.file_indicators, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    parts = [p.strip() for p in line.split(",") if p.strip()]
                    ind_t = parts[0]                        # indicator title
                    ind_p = [int(x) for x in parts[1:]]     # indicator parameters
                    indicators.append({"ind_t":ind_t, "ind_p":ind_p})
        return indicators

    def load_confirmations(self):
        return [
            {"ind_t": "SMA", "ind_p": [5]},
            {"ind_t": "SMA", "ind_p": [10]},
            {"ind_t": "SMA", "ind_p": [20]},
            {"ind_t": "SMA", "ind_p": [50]},
            {"ind_t": "SMA", "ind_p": [100]},
            {"ind_t": "SMA", "ind_p": [200]},
        ]

    def download_data(self, ticker, start, end):
        # collect OHLCVDS data from Yahoo Finance
        try:
            df = yf.download(ticker, start, end, auto_adjust=True)
        except Exception as err:
            raise RuntimeError("Unexpected error in download_data.") from err
        df.columns = df.columns.droplevel(1)    
        df = df[["Close", "Volume"]]
        return df


# =====================================================
#  Indicator
# =====================================================
class Indicator:
    def __init__(self, indicator):
        self.indicator = indicator

    @staticmethod
    def sma(series:pd.Series, window:int) -> pd.Series:
        # simple moving average (SMA)
        return series.rolling(window=window).mean()

    @staticmethod
    def wma(series:pd.Series, window:int) -> pd.Series:
        # weighted moving average (WMA)
        w      = pd.Series(range(1, window+1), dtype=float)
        return series.rolling(window=window).apply(lambda x: (x*w).sum()/w.sum(), raw=True)

    @staticmethod
    def ema(series:pd.Series, window:int) -> pd.Series:
        # exponential moving average (EMA)
        return series.ewm(span=window, adjust=False).mean()

    def setup_indicator(self, df):
        """
        parameters:
        - df: dataframe with column 'Close'
        - indicator: dictionary with
            - ind_t: str with indicator name ("SMA", "WMA", "EMA")
            - ind_p: list with indicator values (10, 20)
        """
        df     = df.copy()
        ind_t  = self.indicator.get("ind_t", "")
        params = self.indicator.get("ind_p", [])

        # function mapping
        ma_fn  = {"SMA": self.sma, "EMA": self.ema, "WMA": self.wma}[ind_t]

        if ind_t in ["SMA", "WMA", "EMA"]:
            # 1 MA
            if len(params) == 1:
                short = params[0]
                df["Short"] = ma_fn( df["Close"], short)
            # 2 MAs
            elif len(params) == 2:
                short, long = params
                df["Short"] = ma_fn( df["Close"], short)
                df["Long"]  = ma_fn( df["Close"], long)
            # 3 MAs
            elif len(params) == 3:
                short, medium, long = params
                df["Short"] = ma_fn( df["Close"], short)
                df["Med"]   = ma_fn( df["Close"], medium)
                df["Long"]  = ma_fn( df["Close"], long)
            else:
                raise ValueError(f"{ind_t} requires 1, 2 or 3 periods, but received {len(params)}.")    
        return df


# =====================================================
#  Backtester
# =====================================================
class Backtester:
    def __init__(self, df):
        self.df = df.copy()

    def run_strategy(self, indicator, ma_v = 10):
        try:
            df     = self.df
            params = indicator["ind_p"]   
    
            # calculate volume MA
            df["VMA"] = df["Volume"].rolling(window=ma_v).mean()        # volume MA

            # generate buy/sell signals
            df["Signal"] = 0
            if len(params) == 1:
                # 1 MA crossover
                df.loc[df["Short"] > df["Close"], "Signal"] = 1         # buy signal  ->  1
                df.loc[df["Short"] < df["Close"], "Signal"] = -1        # sell signal -> -1
            elif len(params) == 2:
                # 2 MAs crossover
                df.loc[df["Short"] > df["Long"], "Signal"] = 1          # buy signal  ->  1
                df.loc[df["Short"] < df["Long"], "Signal"] = -1         # sell signal -> -1
            elif len(params) == 3:
                # 3 MAs crossover
                df.loc[(df["Short"] > df["Med"]) & (df["Med"] > df["Long"]), "Signal"] = 1                              # buy signal  ->  1
                df.loc[(df["Short"] < df["Med"]) & (df["Med"] < df["Long"]), "Signal"] = -1                             # sell signal -> -1
            df["Signal_Length"] = df["Signal"].groupby((df["Signal"] != df["Signal"].shift()).cumsum()).cumcount() +1   # consecutive samples of same signal (signal length)
            df.loc[df["Signal"] == 0, "Signal_Length"] = 0                                                              # length is zero while there is no signal
            df["Volume_Strength"] = (df["Volume"] -df["VMA"])/df["VMA"]                                                 # volume strenght

            # simulate execution (backtest)
            df["Position"] = df["Signal"].shift(1)                      # simulate position (using previous sample)
            df.loc[df["Position"] == -1, "Position"] = 0                # comment if also desired selling operations  
            df["Trade"] = df["Position"].diff().abs()                   # simulate trade
            df["Return"] = df["Close"].pct_change()                     # asset percentage variation (in relation to previous sample)
            df["Strategy"] = df["Position"]*df["Return"]                # return of the strategy
    
            # compare benchmark vs current strategy
            df["Cumulative_Market"] = (1 +df["Return"]).cumprod()       # cumulative return buy & hold strategy
            df["Cumulative_Strategy"] = (1 +df["Strategy"]).cumprod()   # cumulative return current strategy
            df["Cumulative_Trades"] = df["Trade"].cumsum()              # cumulative number of trades
        
            # calculate drawdown
            df["Drawdown"] = (df["Cumulative_Strategy"] -df["Cumulative_Strategy"].cummax())/df["Cumulative_Strategy"].cummax()
            
        
        except KeyError as err:
            raise KeyError(f"Required column missing in backtest: {err}")
        except ZeroDivisionError as err:
            raise RuntimeError("Division by zero in backtest calculations.") from err
        except Exception as err:
            raise RuntimeError(f"Error in backtest run_strategy: {err}") from err
        return df

    def plot_res(self, label):
        ticker, ind_t, *params = label.split("_")

        # save results
        plt.figure(figsize=(12,6))
        plt.plot(self.df.index, self.df["Close"], label=f"{ticker}")
        if "Short" in self.df and len(params) >= 1:
            plt.plot(self.df.index, self.df["Short"], label=f"{ind_t}{params[0]}")
        if "Long" in self.df and len(params) == 2:
            plt.plot(self.df.index, self.df["Long"], label=f"{ind_t}{params[1]}")
        if "Long" in self.df and len(params) >= 3:
            plt.plot(self.df.index, self.df["Long"], label=f"{ind_t}{params[1]}")
        if "Med" in self.df and len(params) >= 3:
            plt.plot(self.df.index, self.df["Med"], label=f"{ind_t}{params[2]}")
        plt.title(f"{ticker} - Price")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"results/{label}.png", dpi=300, bbox_inches="tight")
        plt.close()

        plt.figure(figsize=(12,6))
        plt.plot(self.df.index, self.df["Cumulative_Market"], label="Buy & Hold")
        plt.plot(self.df.index, self.df["Cumulative_Strategy"], label="Strategy")
        plt.title(f"{ticker} - Backtest {ind_t}{'/'.join(params)}")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"results/{label}_backtest.png", dpi=300, bbox_inches="tight")
        plt.close()


# =====================================================
#  Exporter
# =====================================================
class Exporter:
    def export_dataframe(self, pro_data):
        # export dataframe for further analysis
        for ticker, ticker_debug in pro_data.items():
            with pd.ExcelWriter(f"debug/{ticker}.xlsx", engine="openpyxl") as writer:
                for sheet_name, df in ticker_debug.items():
                    # write to .xlsx
                    df.to_excel(writer, sheet_name=sheet_name[:20])

    def export_results(self, res_data):
        # export backtesting results (a spreadsheet for each ticker)
        with pd.ExcelWriter("results/results_backtest.xlsx", engine="openpyxl") as writer:
            for ticker, ticker_results in res_data.items():
                # orient combinations to rows
                ticker_results_df = pd.DataFrame.from_dict(ticker_results, orient="index")

                # write to .xlsx
                ticker_results_df.to_excel(writer, sheet_name=ticker[:10], index=False)

    def export_best_results(self, bst_data):
        # export best results (a spreadsheet for each ticker)
        with pd.ExcelWriter("results/results_best.xlsx", engine="openpyxl") as writer:
            for ticker, bst_df in bst_data.items():
                # write to .xlsx 
                bst_df.to_excel(writer, sheet_name=ticker[:10], index=False)

    def export_report(self, report, end):
        # export report to local
        report_df = pd.DataFrame(report)
        with pd.ExcelWriter("report/report.xlsx", engine="openpyxl") as writer:
            report_df.to_excel(writer, sheet_name=str(end)[:10], index=False)

    def update_best_results(self, bst_data):
        # update best results (for use in b3_trading_signals_bot)
        with open("strategies.csv", "w") as f:
            f.write("Ticker,Indicator,Parameters\n")
            for ticker, bst_df in bst_data.items():
                # write to .csv
                row    = bst_df.iloc[0]
                params = "_".join(str(p) for p in row["Parameters"])
                f.write(f"{ticker},{row['Indicator']},{params}\n")


# =====================================================
#  Strategy Manager
# =====================================================
class Strategies:
    PRESET_DEFAULT = "basic"
    PRESET = {
        "basic":     {"w_return": 1.0, "w_trades": 0.02, "w_sharpe": 0, "w_drdown": 0},
        "balanced":  {"w_return": 1.0, "w_trades": 0.04, "w_sharpe": 0, "w_drdown": 0},
        "agressive": {"w_return": 1.0, "w_trades": 0.04, "w_sharpe": 0.01, "w_drdown": 0.01},
    }
    
    def import_strategies(self, csv_file):
        # import strategies
        strategies = pd.read_csv(csv_file).set_index("Ticker").to_dict("index")
        return strategies

    def best_strategy(self, res_data, preset, **weights):
        bst_data = {}

        if preset not in self.PRESET:
            print(f"Preset not recognized. Using {self.PRESET_DEFAULT}.")
            preset = self.PRESET_DEFAULT

        params = {**self.PRESET[preset], **weights}
        w_return = params["w_return"]
        w_trades = params["w_trades"]
        w_sharpe = params["w_sharpe"]
        w_drdown = params["w_drdown"]
        
        
        for ticker, ticker_results in res_data.items():
            df = pd.DataFrame.from_dict(ticker_results, orient="index")
            
            # calculate SCORE
            df["Score"] = (
                w_return*df["Return_Strategy"]
                -w_trades*df["Trades"]
                +w_sharpe*df["Sharpe"]
                -w_drdown*df["Max_Drawdown"]
            )
            bst_data[ticker] = df.sort_values("Score", ascending=False)
        return bst_data


# =====================================================
#  Notifier
# =====================================================
class Notifier:
    def __init__(self):
        load_dotenv()
        self.TOKEN    = os.getenv("TOKEN")
        self.CHAT_ID  = os.getenv("CHAT_ID")

    def send_telegram(self, msg):
        url     = f"https://api.telegram.org/bot{self.TOKEN}/sendMessage"
        payload = {"chat_id": self.CHAT_ID, "text": msg}
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print("Telegram sent.")