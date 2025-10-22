import os, itertools, sys, traceback
from datetime import datetime
from b3_trading_signals_functions import Loader, Indicator, Strategies, Backtester, Forecaster, Exporter
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    # defines start and end time
    start = "2024-01-01"
    end   = datetime.now()
    
    # defines score profile
    preset = "defensive"

    # initialize cache dictionaries
    raw_data = {}
    pro_data = {}
    res_data = {}

    # import lists of parameters:
    # - tickers
    # - strategies: simple moving average (SMA) combinations
    loader     = Loader("tickers.txt", "indicators.txt")
    tickers    = loader.load_tickers()
    indicators = loader.load_indicators()

    try:
        # download data and run backtest (for each ticker and strategy)
        for ticker, indicator in itertools.product(tickers, indicators):

            # download data (only once)
            if ticker not in raw_data:
                raw_data[ticker] = loader.download_data(ticker, start, end)
            df = raw_data[ticker]

            # setup indicator
            df = Indicator(indicator).setup_indicator(df)

            # predictions
            forecast = Forecaster(df)
            df = forecast.predictions()
            
            # run backtest
            backtest = Backtester(df)
            df = backtest.run_strategy(indicator)
            
            if ticker not in res_data:
                res_data[ticker] = {}
                pro_data[ticker] = {}

            # store processed data and result data
            ind_t  = indicator["ind_t"]  # indicator title
            ind_p  = indicator["ind_p"]  # indicator parameters
            params = "_".join(str(p) for p in ind_p)
            label  = f"{ticker}_{ind_t}_{params}"
        
            pro_data[ticker][label] = df.copy()
            res_data[ticker][label] = {
                "Indicator": ind_t,
                "Parameters": ind_p,
                "Return_Market": df["Cumulative_Market"].iloc[-1],
                "Return_Strategy": df["Cumulative_Strategy"].iloc[-1],
                "Trades": df["Cumulative_Trades"].iloc[-1]//2,
                "Sharpe": df["Strategy"].mean()/df["Strategy"].std()*pow(len(df["Strategy"]), 0.5),
                "Max_Drawdown": abs(df["Drawdown"].min()),
                "Score": 0
            }
            backtest.plot_res(label)

        # compute best strategies (for each ticker)
        bst_data = Strategies().best_strategy(res_data, preset)

        # exports dataframe for analysis
        exporter = Exporter()
        exporter.export_dataframe(pro_data)

        # exports backtesting results
        exporter.export_results(res_data)

        # exports backtesting results sorted by best
        exporter.export_best_results(bst_data)

        # updates best strategies
        exporter.update_best_results(bst_data)
        
    except Exception as err:
        tb = traceback.format_exc()
        print(f"Fatal error in main: {err}\n{tb}.")
        sys.exit(1)


if __name__ == "__main__":
    max_attempt = 3
    
    for attempt in range(1, max_attempt+1):
        try:
            print(f"Attempt {attempt} of {max_attempt}.")
            main()
            break
        except Exception as err:
            print(f"Error on attempt {attempt}: {err}.")
            if attempt == max_attempt:
                print("All attempts failed.")