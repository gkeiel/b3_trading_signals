import os
import itertools
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
        df = tsf.run_strategy(df, ma_s, ma_l)

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
            "Return_Strategy": df["Cumulative_Strategy"].iloc[-1],
            "Trades": df["Cumulative_Trades"].iloc[-1]//2,
            "Score": 0
        }
        tsf.plot_res(df, ticker, ma_s, ma_l)

    # compute best strategies (for each ticker)
    bst_data = tsf.best_strategy(res_data, w_return = 1, w_trades = 0.01)

    # exports dataframe for analysis
    tsf.export_dataframe(pro_data)

    # exports backtesting results
    tsf.export_results(res_data)

    # exports backtesting results sorted by best
    tsf.export_best_results(bst_data)

    # updates best strategies
    tsf.update_best_results(bst_data)


if __name__ == "__main__":
    main()