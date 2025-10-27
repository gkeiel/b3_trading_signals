import os
from datetime import datetime
from core.loader import Loader
from core.indicator import Indicator
from core.backtester import Backtester
from core.forecaster import Forecaster
from core.strategies import Strategies
from core.exporter import Exporter
from core.notifier import Notifier
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# import best strategies from strategies.csv: tickers, indicators
#csv_file   = "data/results/strategies.csv"                                                                   # from local folder
csv_file   = "https://drive.google.com/uc?export=download&id=1uwzEz3XullFI02U8QhsE3BCFGRliRZu2" # from cloud
strategies = Strategies().import_strategies(csv_file)
tickers    = list(strategies.keys())

# import standard indicators for signal confirmation
confirmations = Loader().load_confirmations()

def main():
    # initialize lists
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
        loader = Loader("config.json", "tickers.txt", "indicators.txt")
        df = loader.download_data(ticker)
        confir = []
        for confirmation in confirmations:
            df_c = df.copy()
            df_c = Indicator(confirmation).setup_indicator(df_c)
            df_c = Backtester(df_c).run_strategy(confirmation)
            confir.append(df_c["Signal"].iloc[-1])
        df = Indicator(indicator).setup_indicator(df)
        forecaster = Forecaster(df)
        df = forecaster.predictions()
        df = Backtester(df).run_strategy(indicator)

        # obtain last values: closing price, signal, signal length, volume strength, entry price, forecast
        last_clo = df["Close"].iloc[-1]
        last_sig = df["Signal"].iloc[-1]
        last_str = df["Signal_Length"].iloc[-1]
        last_vol = df["Volume_Strength"].iloc[-1]
        last_ent = df["Entry_Price"].iloc[-1]
        last_for = forecaster.predict_next()
        last_con = confir.count(1)

        # store report
        alerts.append({
            "Ticker": ticker,
            "Indicator": ind_t,
            "Parameters": params,
            "Close": float(last_clo),
            "Signal": int(last_sig),
            "Signal_Length": int(last_str),
            "Signal Confirmation": last_con,
            "Volume_Strength": float(last_vol),
            "Entry_Price": float(last_ent),
            "Predicted_Close": float(last_for)
        })
    
    messages = {}
    for a in alerts:
        # define signal
        if a["Signal"] != 0:       
            verb = "⬆️ BUY" if a["Signal"] == 1 else "⬇️ SELL"
        else:
            verb = "⏸️ NEUTRAL"
        
        # trading message
        msg = (f"#{a['Ticker']} | {verb} ({a['Indicator']}{'/'.join(a['Parameters'])}) Duration {a['Signal_Length']:d} | Price R${a['Close']:.2f}\n"
               f"Volume Strength: {a['Volume_Strength']:.2f}\n"
               f"Signal Confirmation: {a['Signal Confirmation']}/{len(confir)} BUY, {len(confir)-a['Signal Confirmation']}/{len(confir)} SELL\n"
               f"Entry Price: R$ {a['Entry_Price']:.2f}\n"
               f"Predicted Price: R$ {a['Predicted_Close']:.2f}")
        report.append(msg)

        # notifies via Telegram
        notifier = Notifier()
        try:
            payload = {"chat_id": notifier.CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True}
            msg_id  = notifier.send_telegram(payload)
            messages[a["Ticker"]] = msg_id
        except Exception as err:
            print("Telegram error:", err)
    
    # summary in Telegram
    try:
        summary = []
        for ticker, msg_id in messages.items():
            link = f"https://t.me/c/{str(notifier.CHAT_ID).replace('-100', '')}/{msg_id}"   # from private channel
            link = f"https://t.me/{notifier.CHAT_ID.lstrip('@')}/{msg_id}"                  # from public channel
            summary.append(f'<a href="{link}">{ticker}</a>')
        msg   =  " ○ ".join(summary)
        payload = {"chat_id": notifier.CHAT_ID, "text": f"<b>Summary:</b>\n{msg}", "parse_mode": "HTML"}
        sum_id  = notifier.send_telegram(payload)
        
        #payload = {"chat_id": notifier.CHAT_ID, "message_id": sum_id, "disable_notification": True}
        #notifier.pin_telegram(payload)
    except Exception as err:
        print("Telegram error:", err)
        
    # export report
    Exporter().export_report(report)


if __name__ == "__main__":
    main()