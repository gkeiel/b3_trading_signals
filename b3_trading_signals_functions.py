import os
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib 
import requests
from dotenv import load_dotenv
matplotlib.use("Agg")


def load_tickers(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        tickers = [line.strip() for line in f if line.strip()]
    return tickers


def load_indicators(filepath):
    indicators = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                s, l = line.strip().split(",")
                indicators.append((int(s), int(l)))
    return indicators


def download_data(ticker, start, end):
    # collect OHLCVDS data from Yahoo Finance
    df = yf.download(ticker, start, end, auto_adjust=True)
    df.columns = df.columns.droplevel(1)    
    df = df[["Close", "Volume"]]
    return df


def run_strategy(df, ma_s, ma_l, ma_v = 10):
    df = df.copy()
    
    # calculate indicators
    lab_ma_s = f"SMA{ma_s}"
    lab_ma_l = f"SMA{ma_l}"
    lab_ma_v = "VMA"
    df[lab_ma_s] = df["Close"].rolling(window=ma_s).mean()      # short MA
    df[lab_ma_l] = df["Close"].rolling(window=ma_l).mean()      # long MA
    df[lab_ma_v] = df["Volume"].rolling(window=ma_v).mean()     # volume MA

    # generate buy/sell signals
    df["Signal"] = 0
    df.loc[df[lab_ma_s] > df[lab_ma_l], "Signal"] = 1           # buy signal  ->  1
    df.loc[df[lab_ma_s] < df[lab_ma_l], "Signal"] = -1          # sell signal -> -1
    df["Signal_Length"] = df["Signal"].groupby((df["Signal"] != df["Signal"].shift()).cumsum()).cumcount() +1  # consecutive samples of same signal (signal length)
    df.loc[df["Signal"] == 0, "Signal_Strength"] = 0                                                           # strength is zero while there is no signal
    df["Volume_Strength"] = (df["Volume"] -df[lab_ma_v])/df[lab_ma_v]                                          # volume strenght

    # simulate execution (backtest)
    df["Position"] = df["Signal"].shift(1)                      # simulate position (using previous sample)
    df.loc[df["Position"] == -1, "Position"] = 0                # comment if also desired selling operations  
    df["Trade"] = df["Position"].diff().abs()                   # simulate trade
    df["Return"] = df["Close"].pct_change()                     # asset percentage variation (in relation to previous sample)
    df["Strategy"] = df["Position"]*df["Return"]                # return of the strategy
    
    # compare buy & hold vs current strategy
    df["Cumulative_Market"] = (1 +df["Return"]).cumprod()       # cumulative return buy & hold strategy
    df["Cumulative_Strategy"] = (1 +df["Strategy"]).cumprod()   # cumulative return current strategy
    df["Cumulative_Trades"] = df["Trade"].cumsum()              # cumulative number of trades
    return df


def plot_res(df, ticker, ma_s, ma_l):
    # save results
    plt.figure(figsize=(12,6))
    plt.plot(df.index, df["Close"], label=f"{ticker}")
    plt.plot(df.index, df[f"SMA{ma_s}"], label=f"SMA{ma_s}")
    plt.plot(df.index, df[f"SMA{ma_l}"], label=f"SMA{ma_l}")
    plt.title(f"{ticker} - Price")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"results/{ticker}_{ma_s}_{ma_l}.png", dpi=300, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(12,6))
    plt.plot(df.index, df["Cumulative_Market"], label="Buy & Hold")
    plt.plot(df.index, df["Cumulative_Strategy"], label="Strategy")
    plt.title(f"{ticker} - Backtest SMA{ma_s}/{ma_l}")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"results/{ticker}_backtest_{ma_s}_{ma_l}.png", dpi=300, bbox_inches="tight")
    plt.close()


def best_strategy(df, w_return, w_trades):
    df = df.copy()

    df["Score"]     = w_return*df["Return_Strategy"] -w_trades*df["Trades"]
    best_results_df = df.loc[df["Score"].nlargest(3).index].copy()
    return best_results_df


def send_telegram(msg):
    load_dotenv()
    TOKEN   = os.getenv("TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    url     = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    print("Telegram sent.")