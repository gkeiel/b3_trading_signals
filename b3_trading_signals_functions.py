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
                parts = [p.strip() for p in line.split(",") if p.strip()]
                ind_t = parts[0]                    # indicator title
                ind_p = [int(x) for x in parts[1:]] # indicator parameters
                indicators.append({"ind_t":ind_t, "ind_p":ind_p})
    return indicators


def load_confirmations():
    return [
        {"ind_t": "SMA", "ind_p": [5]},
        {"ind_t": "SMA", "ind_p": [10]},
        {"ind_t": "SMA", "ind_p": [20]},
        {"ind_t": "SMA", "ind_p": [50]},
        {"ind_t": "SMA", "ind_p": [100]},
        {"ind_t": "SMA", "ind_p": [200]},
    ]


def download_data(ticker, start, end):
    # collect OHLCVDS data from Yahoo Finance
    df = yf.download(ticker, start, end, auto_adjust=True)
    df.columns = df.columns.droplevel(1)    
    df = df[["Close", "Volume"]]
    return df


def sma(series:pd.Series, window:int) -> pd.Series:
    # simple moving average (SMA)
    return series.rolling(window=window).mean()


def wma(series:pd.Series, window:int) -> pd.Series:
    # weighted moving average (WMA)
    w      = pd.Series(range(1, window+1), dtype=float)
    return series.rolling(window=window).apply(lambda x: (x*w).sum()/w.sum(), raw=True)


def ema(series:pd.Series, window:int) -> pd.Series:
    # exponential moving average (EMA)
    return series.ewm(span=window, adjust=False).mean()


def setup_indicator(df, indicator):
    """
    parameters:
    - df: dataframe with column 'Close'
    - indicator: dictionary with
        - ind_t: str with indicator name ("SMA", "WMA", "EMA")
        - ind_p: list with indicator values (10, 20)

    """
    ind_t  = indicator.get("ind_t", "")
    params = indicator.get("ind_p", [])

    # function mapping
    ma_fn  = {"SMA": sma, "EMA": ema, "WMA": wma}[ind_t]

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


def run_strategy(df, indicator, ma_v = 10):
    ind_t  = indicator["ind_t"]
    params = indicator["ind_p"]   
    
    # calculate volume MA
    df["VMA"] = df["Volume"].rolling(window=ma_v).mean()        # volume MA

    # generate buy/sell signals
    df["Signal"] = 0
    if len(params) == 1:
        # 1 MA crossover
        df.loc[df["Short"] > df["Close"], "Signal"] = 1        # buy signal  ->  1
        df.loc[df["Short"] < df["Close"], "Signal"] = -1       # sell signal -> -1
    if len(params) == 2:
        # 2 MAs crossover
        df.loc[df["Short"] > df["Long"], "Signal"] = 1          # buy signal  ->  1
        df.loc[df["Short"] < df["Long"], "Signal"] = -1         # sell signal -> -1
    elif len(params) == 3:
        # 3 MAs crossover
        df.loc[(df["Short"] > df["Med"]) & (df["Med"] > df["Long"]), "Signal"] = 1                              # buy signal  ->  1
        df.loc[(df["Short"] < df["Med"]) & (df["Med"] < df["Long"]), "Signal"] = -1                             # sell signal -> -1
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
    ticker, ind_t, *params = label.split("_")

    # save results
    plt.figure(figsize=(12,6))
    plt.plot(df.index, df["Close"], label=f"{ticker}")
    if "Short" in df and len(params) >= 1:
        plt.plot(df.index, df["Short"],  label=f"{ind_t}{params[0]}")
    if "Med" in df and len(params) >= 2:
        plt.plot(df.index, df["Med"], label=f"{ind_t}{params[1]}")
    if "Long" in df and len(params) >= 3:
        plt.plot(df.index, df["Long"],   label=f"{ind_t}{params[2]}")
    plt.title(f"{ticker} - Price")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"results/{label}.png", dpi=300, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(12,6))
    plt.plot(df.index, df["Cumulative_Market"], label="Buy & Hold")
    plt.plot(df.index, df["Cumulative_Strategy"], label="Strategy")
    plt.title(f"{ticker} - Backtest {ind_t}{'/'.join(params)}")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"results/{label}_backtest.png", dpi=300, bbox_inches="tight")
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
        f.write("Ticker,Indicator,Parameters\n")
        for ticker, bst_df in bst_data.items():
            # write to .csv
            row    = bst_df.iloc[0]
            params = "_".join(str(p) for p in row["Parameters"])
            f.write(f"{ticker},{row['Indicator']},{params}\n")


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