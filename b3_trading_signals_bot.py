import os
from datetime import datetime
from b3_trading_signals_functions import Loader, Indicator, Strategies, Backtester, Exporter, Notifier
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# import best strategies from strategies.csv: tickers, indicators
#csv_file   = "strategies.csv"                                                                   # from local folder
csv_file   = "https://drive.google.com/uc?export=download&id=1uwzEz3XullFI02U8QhsE3BCFGRliRZu2" # from cloud
strategies = Strategies().import_strategies(csv_file)
tickers    = list(strategies.keys())

# import standard indicators for signal confirmation
confirmations = Loader().load_confirmations()

def main():
    # define start and end time
    start  = "2025-06-01"
    end    = datetime.now()
    alerts = []
    report = []

    # run for each ticker
    for ticker in tickers:
        print(f"Processing {ticker}")
        
        # strategy
        ind_t     = strategies[ticker]["Indicator"]
        ind_p     = strategies[ticker]["Parameters"]
        params    = ind_p.split("_")
        indicator = {"ind_t": ind_t, "ind_p": [int(p) for p in params]}
        
        # download and backtest
        loader = Loader("tickers.txt", "indicators.txt")
        df = loader.download_data(ticker, start, end)
        conf = []
        for confirmation in confirmations:
            df_c = df.copy()
            df_c = Indicator(indicator).setup_indicator(df_c)
            df_c = Backtester(df_c).run_strategy(confirmation)
            conf.append(df_c["Signal"].iloc[-1])
        df = Indicator(indicator).setup_indicator(df)
        df = Backtester(df).run_strategy(indicator)

        # obtain last: price, signal, signal length, volume strength
        last_clo = df["Close"].iloc[-1]
        last_sig = df["Signal"].iloc[-1]
        last_str = df["Signal_Length"].iloc[-1]
        last_vol = df["Volume_Strength"].iloc[-1]
        last_con = conf.count(1)

        # store report
        alerts.append({
            "Ticker": ticker,
            "Indicator": ind_t,
            "Parameters": params,
            "Close": float(last_clo),
            "Signal": int(last_sig),
            "Signal_Length": int(last_str),
            "Signal Confirmation": last_con,
            "Volume_Strength": float(last_vol)
        })
    
    for a in alerts:
        # trading signal message
        if a["Signal"] != 0:       
            verb = "⬆️ BUY" if a["Signal"] == 1 else "⬇️ SELL"
        else:
            verb = "⏸️ NEUTRAL"
        msg = (f"{a['Ticker']} | {verb} ({a['Indicator']}{'/'.join(a['Parameters'])}) Duration {a['Signal_Length']:d} | Price R${a['Close']:.2f}\n"
               f"Volume Strength: {a['Volume_Strength']:.2f}\n"
               f"Signal Confirmation: {a['Signal Confirmation']}/{len(conf)} BUY, {len(conf)-a['Signal Confirmation']}/{len(conf)} SELL")
        report.append(msg)

        # notifies via Telegram
        notifier = Notifier()
        try:
            notifier.send_telegram(msg)
        except Exception as err:
            print("Telegram error:", err)

    # export report
    Exporter().export_report(report, end)


if __name__ == "__main__":
    main()