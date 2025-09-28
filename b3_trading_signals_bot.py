import os
import b3_trading_signals_functions as tsf
from datetime import datetime
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# import strategies from strategies.csv: tickers, indicators
csv_file   = "strategies.csv"                                                                   # from local folder
csv_file   = "https://drive.google.com/uc?export=download&id=1uwzEz3XullFI02U8QhsE3BCFGRliRZu2" # from cloud
strategies = tsf.import_strategies(csv_file)
tickers    = list(strategies.keys())


def main():
    # define start and end time
    start  = "2025-06-01"
    end    = datetime.now().strftime("%Y-%m-%d")
    alerts = []
    report = []

    # run for each ticker
    for ticker in tickers:
        print(f"Processing {ticker}")
        
        # strategy
        ma_s = strategies[ticker]["MA_S"]
        ma_l = strategies[ticker]["MA_L"]

        # download and backtest
        df = tsf.download_data(ticker, start, end)
        df = tsf.run_strategy(df, ma_s, ma_l)

        # obtain last: price, signal, signal strength
        last_clo = df["Close"].iloc[-1]
        last_sig = df["Signal"].iloc[-1]
        last_str = df["Signal_Length"].iloc[-1]
        last_vol = df["Volume_Strength"].iloc[-1]
        
        # store report
        alerts.append({
            "Ticker": ticker,
            "MA_S": ma_s,
            "MA_L": ma_l,
            "Close": float(last_clo),
            "Signal": int(last_sig),
            "Signal_Length": int(last_str),
            "Volume_Strength": float(last_vol)
        })
    
    for a in alerts:
        if a["Signal"] != 0:       
            # trading signal message
            verb = "⬆️ BUY" if a["Signal"] == 1 else "⬇️ SELL"
            msg  = f"{a['Ticker']} | {verb} (SMA{a['MA_S']}/{a['MA_L']}) Duration {a['Signal_Length']:d} | Volume Strength {a['Volume_Strength']:.2f} | Price R${a['Close']:.2f}"
            report.append(msg)
                
            # notifies via Telegram
            try:
                tsf.send_telegram(msg)
            except Exception as err:
                print("Telegram error:", err)

    # export report
    tsf.export_report(report, end)


if __name__ == "__main__":
    main()