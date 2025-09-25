import os
import itertools
import pandas as pd
import b3_trading_signals_functions as tsf
from datetime import datetime
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    # defines start and end time
    start = "2024-01-01"
    end   = datetime.now()

    # initialize cache dictionaries
    raw_data = {}
    pro_data = {}
    res_data = {}

    # import lists of parameters:
    # - tickers
    # - strategies: simple moving average (SMA) combinations
    tickers    = tsf.load_tickers("tickers.txt")
    indicators = tsf.load_indicators("indicators.txt")

    # download data and run backtest (for each ticker and strategy)
    for ticker, (ma_s, ma_l) in itertools.product(tickers, indicators):

        # download data (only once)
        if ticker not in raw_data:
            raw_data[ticker] = tsf.download_data(ticker, start, end)
        df = raw_data[ticker]

        # run backtest
        df = tsf.run_strategy(df[["Close"]], ma_s, ma_l)

        if ticker not in res_data:
            res_data[ticker] = {}
            pro_data[ticker] = {}

        # store processed data and result data
        label = f"{ticker}_{ma_s}_{ma_l}"
        pro_data[ticker][label] = df.copy()
        res_data[ticker][label] = {
            "MA_Short": ma_s,
            "MA_Long": ma_l,
            "Return_Market": df["Cumulative_Market"].iloc[-1],
            "Return_Strategy": df["Cumulative_Strategy"].iloc[-1]
        }
        tsf.plot_res(df, ticker, ma_s, ma_l)

    # export dataframe for further analysis
    for ticker, ticker_debug in pro_data.items():
        with pd.ExcelWriter(f"debug/{ticker}.xlsx", engine="openpyxl") as writer:
            for sheet_name, df in ticker_debug.items():
                df.to_excel(writer, sheet_name=sheet_name[:15])

    # export results (a spreadsheet for each ticker)
    with pd.ExcelWriter("results/results_backtest.xlsx", engine="openpyxl") as writer:
        for ticker, ticker_results in res_data.items():
            ticker_results_df = pd.DataFrame.from_dict(ticker_results, orient="index")
            ticker_results_df.to_excel(writer, sheet_name=ticker[:10], index=False)


if __name__ == "__main__":
    main()