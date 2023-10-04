from datetime import datetime
from typing import Dict, List, Optional, Callable
from copy import deepcopy

import efinance as ef
from pandas import DataFrame

from vnpy.trader.datafeed import BaseDatafeed
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData, HistoryRequest
from vnpy.trader.utility import round_to, ZoneInfo

# 股票支持列表
STOCK_LIST: List[Exchange] = [
    Exchange.SSE,
    Exchange.SZSE,
    Exchange.BSE,
]

# 期货支持列表
FUTURE_LIST: List[Exchange] = [
    Exchange.CFFEX,
    Exchange.SHFE,
    Exchange.CZCE,
    Exchange.DCE,
    Exchange.INE,
]

# 交易所映射
EXCHANGE_VT2EF: Dict[Exchange, str] = {
    Exchange.CFFEX: "8",
    Exchange.SHFE: "113",
    Exchange.CZCE: "115",
    Exchange.DCE: "114",
    Exchange.INE: "142",
    Exchange.GFEX: "225",
    Exchange.SSE: "SSE",
    Exchange.SZSE: "SZSE",
}

# 时间调整映射
INTERVAL_ADJUSTMENT_MAP: Dict[Interval, int] = {
    Interval.MINUTE: 1,
    # Interval.MINUTE_5: 5,
    # Interval.MINUTE_15: 15,
    # Interval.MINUTE_30: 30,
    Interval.HOUR: 60,
    Interval.DAILY: 101,
    Interval.WEEKLY: 102,
    # Interval.MONTH: 103
}

# 中国上海时区
CHINA_TZ = ZoneInfo("Asia/Shanghai")


def to_ef_symbol(symbol, exchange) -> Optional[str]:
    """将交易所代码转换为efinance代码"""
    # 股票
    if exchange in STOCK_LIST:
        ts_symbol: str = f"{symbol}"
    # 期货
    elif exchange in FUTURE_LIST:
        ts_symbol: str = f"{EXCHANGE_VT2EF[exchange]}.{symbol}".lower()
    else:
        return None

    return ts_symbol


def to_ef_quote(exchange):
    """选择股票和期货"""
    if exchange in STOCK_LIST:
        datafeed = getattr(ef, 'stock')
    # 期货
    elif exchange in FUTURE_LIST:
        datafeed = getattr(ef, 'futures')
    else:
        return None

    return datafeed


class EfinanceDatafeed(BaseDatafeed):
    """Efinance数据服务接口"""

    def __init__(self):
        """"""
        self.inited: bool = False

    def init(self, output: Callable = print) -> bool:
        """初始化"""
        if self.inited:
            return True

        self.inited = True

        return True

    def query_bar_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[BarData]]:
        """查询k线数据"""
        if not self.inited:
            self.init(output)

        symbol: str = req.symbol
        exchange: Exchange = req.exchange
        interval: Interval = req.interval
        start: datetime = req.start.strftime("%Y%m%d")
        end: datetime = req.end.strftime("%Y%m%d")

        ef_symbol: str = to_ef_symbol(symbol, exchange)
        if not ef_symbol:
            return None

        ef_interval: str = INTERVAL_ADJUSTMENT_MAP.get(interval)
        if not ef_interval:
            return None

        datafeed = to_ef_quote(exchange)

        try:
            d1: DataFrame = datafeed.get_quote_history(ef_symbol, beg=start, end=end, klt=ef_interval)
        except IOError as ex:
            output(f"发生输入/输出错误：{ex}")
            return []

        df: DataFrame = deepcopy(d1)

        # 处理原始数据中的NaN值
        df.fillna(0, inplace=True)
        bar_keys: List[datetime] = []
        bar_dict: Dict[datetime, BarData] = {}
        data: List[BarData] = []

        if df is not None:
            for _, row in df.iterrows():
                symbol = symbol
                exchange = exchange

                if interval.value == "d" or interval.value == 'w' or interval.value == 'm':
                    dt: str = row["日期"]
                    dt: datetime = datetime.strptime(dt, "%Y-%m-%d")
                else:
                    dt: str = row["日期"]
                    dt: datetime = datetime.strptime(dt, "%Y-%m-%d %H:%M")

                dt = dt.replace(tzinfo=CHINA_TZ)

                volume = row['成交量']
                turnover = row['换手率']
                open_interest = 0
                open_price = row['开盘']
                high_price = row['最高']
                low_price = row['最低']
                close_price = row['收盘']

                bar: BarData = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    datetime=dt,
                    interval=interval,
                    volume=float(volume),
                    open_price=round_to(open_price, 0.000001),
                    high_price=round_to(high_price, 0.000001),
                    low_price=round_to(low_price, 0.000001),
                    close_price=round_to(close_price, 0.000001),
                    turnover=float(turnover),
                    open_interest=float(open_interest),
                    gateway_name="EF",
                )

                bar_dict[dt] = bar

            bar_keys: list = bar_dict.keys()
            bar_keys = sorted(bar_keys, reverse=False)
            for i in bar_keys:
                data.append(bar_dict[i])

        return data
