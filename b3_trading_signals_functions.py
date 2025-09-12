import os
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib 
import smtplib
import requests
from dotenv import load_dotenv
matplotlib.use("Agg")


def load_tickers(filepath="tickers.txt"):
    with open(filepath, "r", encoding="utf-8") as f:
        tickers = [line.strip() for line in f if line.strip()]
    return tickers


def load_ma_comb(filepath="ma_comb.txt"):
    ma_comb = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                s, l = line.strip().split(",")
                ma_comb.append((int(s), int(l)))
    return ma_comb


def download_data(ticker, start, end):
    # collect OHLCVDS data from Yahoo Finance
    df = yf.download(ticker, start, end, auto_adjust=True)
    df = df[["Close"]]
    return df


def run_strategy(df, ma_s, ma_l):
    df = df.copy()
    
    # calculate indicators
    lab_ma_s = f"SMA{ma_s}"
    lab_ma_l = f"SMA{ma_l}"
    df[lab_ma_s] = df["Close"].rolling(window=ma_s).mean()      # short MA
    df[lab_ma_l] = df["Close"].rolling(window=ma_l).mean()      # long MA
    
    # generate buy/sell signals
    df["Signal"] = 0
    df.loc[df[lab_ma_s] > df[lab_ma_l], "Signal"] = 1           # buy signal
    df.loc[df[lab_ma_s] < df[lab_ma_l], "Signal"] = -1          # sell signal
    
    # simulate execution (backtest)
    df["Position"] = df["Signal"].shift(1)                      # position based in signal from previous sample
    df["Return"] = df["Close"].pct_change()                     # asset percentage variation in relation to previous sample
    df["Strategy"] = df["Position"]*df["Return"]                # return of the strategy
    
    # compare buy & hold vs current strategy
    df["Cumulative_Market"] = (1 +df["Return"]).cumprod()       # cumulative return buy & hold strategy
    df["Cumulative_Strategy"] = (1 +df["Strategy"]).cumprod()   # cumulative return current strategy
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


def send_telegram(msg):
    load_dotenv()
    TOKEN   = os.getenv("TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    url     = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    print("Telegram sent.") 