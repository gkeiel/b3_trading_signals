import os
import pandas as pd
import b3_trading_signals_functions as tsf
from datetime import datetime
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# insert best strategy
ma_s = 10
ma_l = 20
pair = (ma_s, ma_l)

def main():
    # define start and end time
    start  = "2023-01-01"
    end    = datetime.now().strftime("%Y-%m-%d")
    alerts = []

    # import parameters:
    # - tickers
    tickers = tsf.load_tickers("tickers_test.txt") 

    # run for each ticker
    for ticker in tickers:
        print("Processing")

        # download and backtest
        df = tsf.download_data(ticker, start, end)
        df = tsf.run_strategy(df[["Close"]], pair[0], pair[1])

        # verify last: price, signal, signal strength
        last_clo = df["Close"].iloc[-1]
        last_sig = df["Signal"].iloc[-1]
        last_str = df["Signal_Strength"].iloc[-1]
        
        # store report
        alerts.append({
            "Ticker": ticker,
            "MA_S": pair[0],
            "MA_L": pair[1],
            "Close": float(last_clo.iloc[0]),
            "Signal": int(last_sig),
            "Signal_Strength": int(last_str)
        })

        report = [f"Report: {end}", f"SMA: {pair[0]}/{pair[1]}", ""]
        for a in alerts:
            s = a["Signal"]
            line = f"{a['Ticker']}: Signal={s}, Signal={a['Signal_Strength']}, Close={a['Close']:.2f}"
            report.append(line)
        
            if s != 0:
                # trading signal message
                verb = "⬆️ BUY" if s == 1 else "⬇️ SELL"
                msg  = f"{a['Ticker']} | {verb} (SMA{a['MA_S']}/{a['MA_L']}) Strength {a['Signal_Strength']:d} | Price R${a['Close']:.2f}"
                
                # notifies via e-mail
                try:
                    tsf.send_telegram(msg)
                except Exception as err:
                    print("Telegram error:", err)

        # export report
        report_df = pd.DataFrame(report)
        report_df.to_excel("report/report.xlsx", index=False)


if __name__ == "__main__":
    main()