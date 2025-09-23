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

    # initialize dictionaries
    data_cache = {}
    results    = {} 

    # import lists of parameters:
    # - tickers
    # - strategies: simple moving average (SMA) combinations
    tickers    = tsf.load_tickers("tickers_test.txt")
    indicators = tsf.load_indicators("indicators_test.txt")

    # download data and run backtest (for each ticker and strategy)
    for ticker, (ma_s, ma_l) in itertools.product(tickers, indicators):

        # download data (only once)
        if ticker not in data_cache:
            data_cache[ticker] = tsf.download_data(ticker, start, end)
        df = data_cache[ticker]

        # run backtest
        df = tsf.run_strategy(df[["Close"]], ma_s, ma_l)

        # export dataframe for further analysis (optional)
        df.to_excel(f"debug/df_{ticker}_{ma_s}_{ma_l}.xlsx", index=True)

        # initialize ticker list
        if ticker not in results:
            results[ticker] = []
        
        # store results
        results[ticker].append({
            "MA_Short": ma_s,
            "MA_Long": ma_l,
            "Return_Market": df["Cumulative_Market"].iloc[-1],
            "Return_Strategy": df["Cumulative_Strategy"].iloc[-1]
        })
        tsf.plot_res(df, ticker, ma_s, ma_l)

    # export results (a spreadsheet for each ticker)
    with pd.ExcelWriter("results/results_backtest.xlsx", engine="openpyxl") as writer:
        for ticker, ticker_results in results.items():
            ticker_results_df = pd.DataFrame(ticker_results)
            ticker_results_df.to_excel(writer, sheet_name=ticker[:10], index=False)


if __name__ == "__main__":
    main()