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

    def setup_indicator(self, df):
        """
        parameters:
        - df: dataframe with column 'Close'
        - indicator: dictionary with
            - ind_t: str with indicator name ("SMA", "WMA", "EMA")
            - ind_p: list with indicator values (10, 20)
        """
        df     = df.copy()
        ind_t  = self.indicator.get("ind_t", "")
        params = self.indicator.get("ind_p", [])

        # function mapping
        ma_fn  = {"SMA": self.sma, "EMA": self.ema, "WMA": self.wma}[ind_t]

        if ind_t in ["SMA", "WMA", "EMA"]:
            # 1 MA
            if len(params) == 1:
                short = params[0]
                df["Short"] = ma_fn( df["Close"], short)
            # 2 MAs
            elif len(params) == 2:
                short, long = params
                df["Short"] = ma_fn( df["Close"], short)
                df["Long"]  = ma_fn( df["Close"], long)
            # 3 MAs
            elif len(params) == 3:
                short, medium, long = params
                df["Short"] = ma_fn( df["Close"], short)
                df["Med"]   = ma_fn( df["Close"], medium)
                df["Long"]  = ma_fn( df["Close"], long)
            else:
                raise ValueError(f"{ind_t} requires 1, 2 or 3 periods, but received {len(params)}.")    
        return df