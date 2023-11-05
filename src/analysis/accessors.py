from datetime import date
from types import SimpleNamespace

import pandas as pd


class DType(SimpleNamespace):
    U8 = "UInt8"
    U16 = "UInt16"
    U32 = "UInt32"
    CAT = "category"
    DT64 = "datetime64[ns]"


@pd.api.extensions.register_dataframe_accessor("calendar")
class CalendarAccessor:
    def __init__(self, df):
        assert "date" in df or df.index.name == "date"
        self.df = df
        try:
            self.dates = df["date"]
        except KeyError:
            self.dates = df.index

    def __call__(self, join=False):
        cal = self.dates.dt.isocalendar()
        cal["season_week"] = cal.groupby(["year", "week"]).ngroup()
        cal = cal.astype(DType.U16)
        cal["week_start"] = pd.to_datetime(
            cal.apply(lambda x: date.fromisocalendar(x["year"], x["week"], 1), axis=1)
        )
        if join:
            return self.df.join(cal)
        return cal


@pd.api.extensions.register_dataframe_accessor("vol")
class VolumeAccessor:
    def __init__(self, df):
        self.df = df

    def __call__(self, value):
        return self.df[self.df.volume > value]

    def calculate(self):
        data = self.df.loc[:, ["arrows", "secs", "reps"]].fillna(0)
        return (data.arrows + data.secs // 10 + data.reps // 2).astype(int)

    def daily(self, index=False):
        return self.df.groupby("date", as_index=index)["volume"].sum()

    # def label_poundage(self):
    #     bins = pd.IntervalIndex.from_tuples(Poundage.bounds)
    #     result = pd.cut(self.df.lbs, bins)
    #     return result.cat.rename_categories(Poundage.labels)

    @staticmethod
    def ewm(series, span):
        return series.ewm(span=span, adjust=False).mean().rename(span)

    def ewm_multi(self, series, spans):
        return pd.concat([self.ewm(series, n) for n in spans], axis=1)


def init():
    pass
