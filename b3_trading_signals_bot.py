import os
import pandas as pd
import b3_trading_signals_functions as tsf
from datetime import datetime
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# import strategies in strategies.csv: tickers, indicators
# from local folder
csv_file   = "strategies.csv"
# from url
csv_file   = "https://drive.google.com/uc?export=download&id=1uwzEz3XullFI02U8QhsE3BCFGRliRZu2"

strategies = pd.read_csv(csv_file).set_index("Ticker").to_dict("index")
tickers    = list(strategies.keys())


def main():
    # define start and end time
    start  = "2024-01-01"
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
    
    for a in alerts:
        s = a["Signal"]

        if s != 0:       
            # trading signal message
            verb = "⬆️ BUY" if s == 1 else "⬇️ SELL"
            msg  = f"{a['Ticker']} | {verb} (SMA{a['MA_S']}/{a['MA_L']}) Strength {a['Signal_Strength']:d} | Price R${a['Close']:.2f}"
            report.append(msg)
                
            # notifies via Telegram
            try:
                tsf.send_telegram(msg)
            except Exception as err:
                print("Telegram error:", err)

    # export current report
    report_df = pd.DataFrame({f"Report: {end}": report})
    with pd.ExcelWriter("report/report.xlsx", engine="openpyxl") as writer:
        report_df.to_excel(writer, sheet_name=end, index=False)


if __name__ == "__main__":
    main()