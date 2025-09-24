import os
import pandas as pd
import b3_trading_signals_functions as tsf
from datetime import datetime
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# import selected strategies:
# - tickers
# - indicators
strategies = pd.read_csv("strategies.csv").set_index("Ticker").to_dict("index")
tickers    = list(strategies.keys())


def main():
    # define start and end time
    start  = "2024-01-01"
    end    = datetime.now().strftime("%Y-%m-%d")
    alerts = []

    # run for each ticker
    for ticker in tickers:
        print(f"Processing {ticker}")
        
        # strategy
        ma_s = strategies[ticker]["MA_S"]
        ma_l = strategies[ticker]["MA_L"]

        # download and backtest
        df = tsf.download_data(ticker, start, end)
        df = tsf.run_strategy(df[["Close"]], ma_s, ma_l)

        # obtain last: price, signal, signal strength
        last_clo = df["Close"].iloc[-1]
        last_sig = df["Signal"].iloc[-1]
        last_str = df["Signal_Strength"].iloc[-1]
        
        # store report
        alerts.append({
            "Ticker": ticker,
            "MA_S": ma_s,
            "MA_L": ma_l,
            "Close": float(last_clo.iloc[0]),
            "Signal": int(last_sig),
            "Signal_Strength": int(last_str)
        })
        report = [f"Report: {end}", f"SMA: {ma_s}/{ma_l}", ""]
    
    for a in alerts:
        s = a["Signal"]
        line = f"{a['Ticker']}: Signal={s}, Strength={a['Signal_Strength']}, Close={a['Close']:.2f}"
        report.append(line)
        
        if s != 0:
            # trading signal message
            verb = "⬆️ BUY" if s == 1 else "⬇️ SELL"
            msg  = f"{a['Ticker']} | {verb} (SMA{a['MA_S']}/{a['MA_L']}) Strength {a['Signal_Strength']:d} | Price R${a['Close']:.2f}"
                
            # notifies via Telegram
            try:
                tsf.send_telegram(msg)
            except Exception as err:
                print("Telegram error:", err)

    # export current report
    report_df = pd.DataFrame(report)
    report_df.to_excel("report/report.xlsx", index=False)


if __name__ == "__main__":
    main()