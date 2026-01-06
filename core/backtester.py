import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# =====================================================
#  Backtester
# =====================================================
class Backtester:
    def __init__(self, df, file_config="config.json"):
        self.df = df.copy()
        self.load_config(file_config)
        
    def load_config(self, path):
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
            cfg    = config.get("backtest", {})
            
        self.ma_v = cfg.get("ma_volume", 10)

    def run_strategy(self, indicator):
        try:
            df     = self.df
            ind_t  = indicator["ind_t"]
            params = indicator["ind_p"]   
    
            # calculate volume MA
            df["VMA"] = df["Volume"].rolling(window=self.ma_v).mean()        # volume MA

            # generate buy/sell signals
            df["Signal"] = 0
            if ind_t in ["SMA", "EMA", "WMA"]:
                if len(params) == 1:
                    # 1 MA crossover
                    df.loc[df["Close"] > df["Short"], "Signal"] = 1         # buy signal (MA)
                    df.loc[df["Close"] < df["Short"], "Signal"] = -1        # sell signal (MA)
                elif len(params) == 2:
                    # 2 MAs crossover
                    df.loc[df["Short"] > df["Long"], "Signal"] = 1          
                    df.loc[df["Short"] < df["Long"], "Signal"] = -1         
                elif len(params) == 3:
                    # 3 MAs crossover
                    df.loc[(df["Short"] > df["Med"]) & (df["Med"] > df["Long"]), "Signal"] = 1
                    df.loc[(df["Short"] < df["Med"]) & (df["Med"] < df["Long"]), "Signal"] = -1
            elif ind_t == "BB":
                df.loc[df["Close"] < df["BB_Lower"], "Signal"] = 1          # buy signal (BB)
                df.loc[df["Close"] > df["BB_Upper"], "Signal"] = -1         # seel signal (BB)
            elif ind_t == "MACD":
                df.loc[df["MACD"] > df["MACD_Signal"], "Signal"] = 1        # buy signal (MACD)
                df.loc[df["MACD"] < df["MACD_Signal"], "Signal"] = -1       # sell signal (MACD)
            
            df["Signal_Length"] = df["Signal"].groupby((df["Signal"] != df["Signal"].shift()).cumsum()).cumcount() +1   # consecutive samples of same signal (signal length)
            df.loc[df["Signal"] == 0, "Signal_Length"] = 0                                                              # length is zero while there is no signal
            df["Volume_Strength"] = (df["Volume"] -df["VMA"])/df["VMA"]                                                 # volume strenght

            # simulate execution (backtest)
            df["Position"] = df["Signal"].shift(1)                      # simulate position (using previous sample)
            df.loc[df["Position"] == -1, "Position"] = 0                # comment if also desired selling operations  
            df["Trade"] = df["Position"].diff().abs()                   # simulate trade
            df["Entry_Price"] = df["Close"].where(df["Trade"] == 1)     # entry price
            df["Entry_Price"] = df["Entry_Price"].ffill()
            df["Return"] = df["Close"].pct_change()                     # asset percentage variation (in relation to previous sample)
            df["Strategy"] = df["Position"]*df["Return"]                # return of the strategy
            df["Strategy"] = df["Strategy"].fillna(0.00001)
            
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

    def plot_price(self, axis, ticker):
        axis.plot(self.df.index, self.df["Close"], label=ticker)
        axis.grid(True)
    
    def plot_ma(self, axis, ind_t, params):
        if "Short" in self.df and len(params) >= 1:
            axis.plot(self.df.index, self.df["Short"], label=f"{ind_t}{params[0]}")
        if "Long" in self.df and len(params) == 2:
            axis.plot(self.df.index, self.df["Long"], label=f"{ind_t}{params[1]}")
        if "Long" in self.df and len(params) >= 3:
            axis.plot(self.df.index, self.df["Long"], label=f"{ind_t}{params[1]}")
        if "Med" in self.df and len(params) >= 3:
             axis.plot(self.df.index, self.df["Mid"], label=f"{ind_t}{params[2]}")
    
    def plot_bb(self, axis, params):
        axis.plot(self.df.index, self.df["BB_Mid"], label=f"BB mean {params[0]}")
        axis.plot(self.df.index, self.df["BB_Upper"], color='r', label=f"BB std {params[1]}")
        axis.plot(self.df.index, self.df["BB_Lower"], color='r')
        
    def plot_macd(self, axis):
        axis.plot(self.df.index, self.df["MACD"], label="MACD")
        axis.plot(self.df.index, self.df["MACD_Signal"], label="MACD_Signal")
        axis.bar(self.df.index, self.df["MACD_Histogram"], color='r', label="Histogram", alpha=0.4)
        axis.axhline(0, linewidth=1)
        axis.grid(True)

    def plot_res(self, label):
        ticker, ind_t, *params = label.split("_")

        # plot price and indicator
        if ind_t in ["SMA", "EMA", "WMA"]:
            fig, axis = plt.subplots(figsize=(12,6))
            self.plot_price(axis, ticker)
            self.plot_ma(axis, ind_t, params)
            axis.legend()
            axis.set_title(f"{ticker} - Price")
        elif ind_t == "BB":
            fig, axis = plt.subplots(figsize=(12,6))
            self.plot_price(axis, ticker)
            self.plot_bb(axis, params)
            axis.legend()
            axis.set_title(f"{ticker} - Price")
        elif ind_t == "MACD":
            fig, (axis_price, axis_macd) = plt.subplots(2, 1, figsize=(12,8), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
            self.plot_price(axis_price, ticker)
            axis_price.set_title(f"{ticker} - Price")
            self.plot_macd(axis_macd)
        plt.tight_layout()
        plt.savefig(f"data/results/{label}.png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # plot returns
        plt.figure(figsize=(12,6))
        plt.plot(self.df.index, self.df["Close"], label=f"{ticker}")
        plt.plot(self.df.index, self.df["Predicted_Close"], label="Predictions")
        plt.title(f"{ticker} - Price")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"data/results/{label}_forecast.png", dpi=300, bbox_inches="tight")
        plt.close()

        plt.figure(figsize=(12,6))
        plt.plot(self.df.index, self.df["Cumulative_Market"], label="Buy & Hold")
        plt.plot(self.df.index, self.df["Cumulative_Strategy"], label="Strategy")
        plt.title(f"{ticker} - Backtest {ind_t}{'/'.join(params)}")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"data/results/{label}_backtest.png", dpi=300, bbox_inches="tight")
        plt.close()