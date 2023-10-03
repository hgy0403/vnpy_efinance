# VeighNa框架的Efinance数据服务接口

<p align="center">
  <img src ="https://vnpy.oss-cn-shanghai.aliyuncs.com/vnpy-logo.png"/>
</p>

<p align="center">
    <img src ="https://img.shields.io/badge/version-1.0.0-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux|macos-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.7|3.8|3.9|3.10-blue.svg"/>
    <img src ="https://img.shields.io/github/license/vnpy/vnpy.svg?color=orange"/>
</p>

## 说明

基于efinance模块的0.5.0版本开发，支持以下中国金融市场的K线数据：只支持获取k线级别的历史数据，暂不支持获取tick级别的历史数据

* 期货：
  * CFFEX：中国金融期货交易所
  * SHFE：上海期货交易所
  * DCE：大连商品交易所
  * CZCE：郑州商品交易所
  * INE：上海国际能源交易中心
* 股票：
  * SSE：上海证券交易所
  * SZSE：深圳证券交易所
  * BSE：北京证券交易所

## 安装

安装环境推荐基于3.0.0版本以上的【[**VeighNa Studio**](https://www.vnpy.com)】。


下载源代码后，解压后在cmd中运行：

```
python setup.py bdist_wheel
```
dist目录下vnpy_efinance-x.x.x-py3-none-any.whl包

```
python -m pip install vnpy_efinance-x.x.x-py3-none-any.whl
```


## 使用

在VeighNa中使用Efinance时，需要在全局配置中填写以下字段信息：

|名称|含义|必填|举例|
|---------|----|---|---|
|datafeed.name|名称|是|efinance|
|datafeed.username|用户名|否||
|datafeed.password|密码|否||

```
from datetime import datetime
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.object import HistoryRequest

# 获取数据服务实例
datafeed = get_datafeed()

req = HistoryRequest(
    # 合约代码
    symbol="600519",
    # 合约所在交易所
    exchange=Exchange.SSE,
    # 历史数据开始时间
    start=datetime(2023, 1, 1),
    # 历史数据结束时间
    end=datetime(2023, 8, 20),
    # 数据时间粒度，默认可选分钟级、小时级和日级，具体选择需要结合该数据服务的权限和需求自行选择
    interval=Interval.DAILY
)
data = datafeed.query_bar_history(req)
print(data)
```
