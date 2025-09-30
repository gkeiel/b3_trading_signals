import os
import yfinance as yf
import pandas as pd
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
                t, s, l = line.strip().split(",")
                indicators.append((t, int(s), int(l)))
    return indicators


def download_data(ticker, start, end):
    # collect OHLCVDS data from Yahoo Finance
    df = yf.download(ticker, start, end, auto_adjust=True)
    df.columns = df.columns.droplevel(1)    
    df = df[["Close", "Volume"]]
    return df


def sma(series:pd.Series, short:int, long:int) -> tuple[pd.Series, pd.Series]:
    # simple moving average (SMA)
    return (series.rolling(window=short).mean(),
            series.rolling(window=long).mean())


def wma(series:pd.Series, short:int, long:int) -> tuple[pd.Series, pd.Series]:
    # weighted moving average (WMA)
    w_s = pd.Series(range(1, short+1), dtype=float)
    w_l = pd.Series(range(1, long+1), dtype=float)
    series_s = series.rolling(window=short).apply(lambda x: (x*w_s).sum()/w_s.sum(), raw=True)
    series_l = series.rolling(window=long).apply(lambda x: (x*w_l).sum()/w_l.sum(), raw=True)
    return (series_s, series_l)


def ema(series:pd.Series, short:int, long:int) -> tuple[pd.Series, pd.Series]:
    # exponential moving average (EMA)
    return (series.ewm(span=short, adjust=False).mean(),
            series.ewm(span=long, adjust=False).mean())


def setup_indicators(df, label):
    ticker, ind_t, ind_s, ind_l = label.split("_")

    if ind_t == "SMA":
        df["Short"], df["Long"] = sma( df["Close"], int(ind_s), int(ind_l))
    elif ind_t == "EMA":
        df["Short"], df["Long"] = ema( df["Close"], int(ind_s), int(ind_l))
    elif ind_t == "WMA":
        df["Short"], df["Long"] = wma( df["Close"], int(ind_s), int(ind_l))
    return df


def run_strategy(df, ma_v = 10):
    df = df.copy()
    
    # calculate volume MA
    df["VMA"] = df["Volume"].rolling(window=ma_v).mean()        # volume MA

    # generate buy/sell signals
    df["Signal"] = 0
    df.loc[df["Short"] > df["Long"], "Signal"] = 1              # buy signal  ->  1
    df.loc[df["Short"] < df["Long"], "Signal"] = -1             # sell signal -> -1
    df["Signal_Length"] = df["Signal"].groupby((df["Signal"] != df["Signal"].shift()).cumsum()).cumcount() +1   # consecutive samples of same signal (signal length)
    df.loc[df["Signal"] == 0, "Signal_Strength"] = 0                                                            # strength is zero while there is no signal
    df["Volume_Strength"] = (df["Volume"] -df["VMA"])/df["VMA"]                                                 # volume strenght

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


def plot_res(df, label):
    ticker, ind_t, ind_s, ind_l = label.split("_")

    # save results
    plt.figure(figsize=(12,6))
    plt.plot(df.index, df["Close"], label=f"{ticker}")
    plt.plot(df.index, df[f"Short"], label=f"{ind_t}{ind_s}")
    plt.plot(df.index, df[f"Long"], label=f"{ind_t}{ind_l}")
    plt.title(f"{ticker} - Price")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"results/{label}.png", dpi=300, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(12,6))
    plt.plot(df.index, df["Cumulative_Market"], label="Buy & Hold")
    plt.plot(df.index, df["Cumulative_Strategy"], label="Strategy")
    plt.title(f"{ticker} - Backtest {ind_t}{ind_s}/{ind_l}")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"results/backtest_{label}.png", dpi=300, bbox_inches="tight")
    plt.close()


def import_strategies(csv_file):
    # import strategies
    strategies = pd.read_csv(csv_file).set_index("Ticker").to_dict("index")
    return strategies


def export_dataframe(pro_data):
    # export dataframe for further analysis
    for ticker, ticker_debug in pro_data.items():
        with pd.ExcelWriter(f"debug/{ticker}.xlsx", engine="openpyxl") as writer:
            for sheet_name, df in ticker_debug.items():
                # write to .xlsx
                df.to_excel(writer, sheet_name=sheet_name[:20])


def export_results(res_data):
    # export backtesting results (a spreadsheet for each ticker)
    with pd.ExcelWriter("results/results_backtest.xlsx", engine="openpyxl") as writer:
        for ticker, ticker_results in res_data.items():
            # orient combinations to rows
            ticker_results_df = pd.DataFrame.from_dict(ticker_results, orient="index")

            # write to .xlsx
            ticker_results_df.to_excel(writer, sheet_name=ticker[:10], index=False)


def export_best_results(bst_data):
    # export best results (a spreadsheet for each ticker)
    with pd.ExcelWriter("results/results_best.xlsx", engine="openpyxl") as writer:
        for ticker, bst_df in bst_data.items():
            # write to .xlsx 
            bst_df.to_excel(writer, sheet_name=ticker[:10], index=False)


def export_report(report, end):
    # export report to local
    report_df = pd.DataFrame({f"Report: {end}": report})
    with pd.ExcelWriter("report/report.xlsx", engine="openpyxl") as writer:
        report_df.to_excel(writer, sheet_name=end, index=False)


def update_best_results(bst_data):
    # update best results (for use in b3_trading_signals_bot)
    with open("strategies.csv", "w") as f:
        f.write("Ticker,Indicator,Short,Long\n")
        for ticker, bst_df in bst_data.items():
            # write to .csv
            row = bst_df.iloc[0]
            f.write(f"{ticker},{row['Indicator']},{int(row['MA_Short'])},{int(row['MA_Long'])}\n")


def best_strategy(res_data, w_return, w_trades):
    bst_data = {}

    for ticker, ticker_results in res_data.items():
        df = pd.DataFrame.from_dict(ticker_results, orient="index")
        # define desired SCORE
        df["Score"]      = w_return*df["Return_Strategy"] -w_trades*df["Trades"]
        bst_data[ticker] = df.sort_values("Score", ascending=False)
    return bst_data


def send_telegram(msg):
    load_dotenv()
    TOKEN   = os.getenv("TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    url     = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    print("Telegram sent.")