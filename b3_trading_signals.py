import os
import itertools
import pandas as pd
import b3_trading_signals_functions as tsf
from datetime import datetime
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    # define start and end time
    start   = "2023-01-01"
    end     = datetime.now()
    results = []

    # import lists of parameters:
    # - tickers
    # - simple moving average (SMA) combinations
    tickers = tsf.load_tickers("tickers_test.txt")
    ma_comb = tsf.load_ma_comb("ma_comb.txt")

    # run backtest for each ticker and strategy
    for ticker, (ma_s, ma_l) in itertools.product(tickers, ma_comb):
        df = tsf.download_data(ticker, start, end)
        df = tsf.run_strategy(df, ma_s, ma_l)
        final_market   = df["Cumulative_Market"].iloc[-1]
        final_strategy = df["Cumulative_Strategy"].iloc[-1]

        # export current dataframe for analysis
        # df.to_excel("debug/df_debug.xlsx", index=True)
        
        # stores results
        results.append({
            "Ticker": ticker,
            "MA_S": ma_s,
            "MA_L": ma_l,
            "Final_Market": final_market,
            "Final_Strategy": final_strategy
        })
        tsf.plot_res(df, ticker, ma_s, ma_l)

    # export results
    results_df = pd.DataFrame(results)
    results_df.to_excel("results/results_backtest.xlsx", index=False)


if __name__ == "__main__":
    main()