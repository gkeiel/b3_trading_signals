import pandas as pd


# =====================================================
#  Indicator
# =====================================================
class Indicator:
    def __init__(self, indicator):
        self.indicator = indicator

    @staticmethod
    def sma(series:pd.Series, window:int) -> pd.Series:
        # simple moving average (SMA)
        return series.rolling(window=window).mean()

    @staticmethod
    def wma(series:pd.Series, window:int) -> pd.Series:
        # weighted moving average (WMA)
        w      = pd.Series(range(1, window+1), dtype=float)
        return series.rolling(window=window).apply(lambda x: (x*w).sum()/w.sum(), raw=True)

    @staticmethod
    def ema(series:pd.Series, window:int) -> pd.Series:
        # exponential moving average (EMA)
        return series.ewm(span=window, adjust=False).mean()
        
    @staticmethod
    def bollinger_bands(series:pd.Series, window:int, std_dev:float=2.0):
        # bollinger bands (BB)
        middle = series.rolling(window=window).mean()
        std    = series.rolling(window=window).std()
        upper  = middle +(std_dev*std)
        lower  = middle -(std_dev*std)
        return middle, upper, lower
    
    @staticmethod
    def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        # moving average convergence divergence (MACD)
        macd_line   = series.ewm(span=fast, adjust=False).mean() -series.ewm(span=slow, adjust=False).mean()
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram   = macd_line -signal_line
        return macd_line, signal_line, histogram
        
    def setup_indicator(self, df):
        """
        parameters:
        - df: dataframe with column 'Close'
        - indicator: dictionary with
            - ind_t: str with indicator name ("SMA", "WMA", "EMA" or "BB")
            - ind_p: list with indicator values (10, 20)
        """
        df     = df.copy()
        ind_t  = self.indicator.get("ind_t", "")
        params = self.indicator.get("ind_p", [])

        if ind_t in ["SMA", "WMA", "EMA"]:
            fn = getattr(self, ind_t.lower())
            # 1 MA
            if len(params) == 1:
                short = params[0]
                df["Short"] = fn(df["Close"], short)
            # 2 MAs
            elif len(params) == 2:
                short, long = params
                df["Short"] = fn(df["Close"], short)
                df["Long"]  = fn(df["Close"], long)
            # 3 MAs
            elif len(params) == 3:
                short, medium, long = params
                df["Short"] = fn(df["Close"], short)
                df["Mid"]   = fn(df["Close"], medium)
                df["Long"]  = fn(df["Close"], long)
        elif ind_t == "BB":
            window, std_dev = params
            df["BB_Mid"], df["BB_Upper"], df["BB_Lower"] = self.bollinger_bands(df["Close"], window, std_dev)
        elif ind_t == "MACD":
            fast, slow, signal = params
            df["MACD"], df["MACD_Signal"], df["MACD_Histogram"] = self.macd(df["Close"], fast, slow, signal)
        else:
            raise ValueError(f"Unsupported indicator: {ind_t}.")    
        return df