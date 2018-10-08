import datetime
from datetime import timedelta
import pandas as pd
import numpy as np


def ROESelect(date, universe=''):
    """
    无现金资产ROE选股, 条件:
    1. ROE=净利润/(净资产-现金净资产)
    2. 近三个报告期归母净利润增速均大于10%
    3. 按最新一年分红率和负债率排序
    4. 改良的ROE取5年平均

    Args:
        universe (list or str): 股票列表（有后缀）
        date (str or datetime): 常见日期格式支持
    Returns:
        list: ROE价值投资法选择的股票

    Examples:
        >> universe = DynamicUniverse('A')
        >> buy_list = ROESelect('20170101',universe)
    """
    if not universe:
        universe = \
        DataAPI.EquGet(equTypeCD=u"A", secID=u"", ticker=u"", listStatusCD=u"L,S,DE,UN", field=u"secID", pandas="1")[
            'secID'].tolist()
    trade_date = date if isinstance(date, datetime.datetime) else datetime.datetime.strptime(date, '%Y%m%d')
    trade_date = trade_date.strftime('%Y%m%d')
    date_previous = str(int(trade_date) - 10000)

    ##净利润表
    income_data = DataAPI.FdmtISGet(ticker=u"", secID=universe, reportType=u"A", endDate=u"", beginDate=u"",
                                    publishDateEnd=u"", publishDateBegin=u"", endDateRep="", beginDateRep="",
                                    beginYear="2013", endYear="", fiscalPeriod="",
                                    field=u"secID,endDate,NIncome,NIncomeAttrP", pandas="1").drop_duplicates(
        ['secID', 'endDate'])
    ### 总资产表
    assets = DataAPI.FdmtBSGet(ticker="", secID=universe, reportType=u"A", endDate=u"", beginDate=u"",
                               publishDateEnd=u"", publishDateBegin=u"", endDateRep="", beginDateRep="",
                               beginYear="2013", endYear="", fiscalPeriod="",
                               field=u"secID,endDate,TAssets,TLiab,cashCEquiv", pandas="1").drop_duplicates(
        subset=['secID', 'endDate'])
    ### 现金资产
    cash_assets = assets['cashCEquiv']
    ### 负债总额
    liab_assets = assets['TLiab']
    ### 总资产
    asset = assets['TAssets']
    ### 5年ROE
    m = (asset - liab_assets - cash_assets).reset_index(drop=True)
    n = income_data['NIncome'].reset_index(drop=True)
    income_data['refined_ROE'] = n / m
    ROE_list = income_data.dropna(axis=0).groupby('secID')['refined_ROE'].mean().sort_values(axis=0, ascending=False)
    print('#####ROE list sort#######')
    print(ROE_list)

    ##4年净利润表
    income_data = DataAPI.FdmtISGet(ticker=u"", secID=universe, reportType=u"A", endDate=u"", beginDate=u"",
                                    publishDateEnd=u"", publishDateBegin=u"", endDateRep="", beginDateRep="",
                                    beginYear="2014", endYear="", fiscalPeriod="",
                                    field=u"secID,endDate,NIncome,NIncomeAttrP", pandas="1").drop_duplicates(
        ['secID', 'endDate']).reset_index(drop=True)
    ### 归母净利润
    growth_rate = income_data.groupby('secID')['NIncomeAttrP'].pct_change(-1)
    income_data['ngrowth_rate'] = growth_rate
    nincome_list = income_data.groupby('secID').filter(lambda x: x['ngrowth_rate'].min() > 0.1).dropna()
    print('#####Net income list sort#######')
    print(nincome_list)

    ### 每股派现(税前)
    fh = DataAPI.EquDivGet(secID=universe, ticker=u"", eventProcessCD=u"", exDivDate="", beginDate=u"2015-12-31",
                           endDate=u"2016-12-31", beginPublishDate=u"", endPublishDate=u"", beginRecordDate=u"",
                           endRecordDate=u"", field=u"secID,endDate,perCashDiv,payCashDate", pandas="1").reset_index(
        drop=True).dropna()
    close_prices = DataAPI.MktEqudAdjGet(beginDate=u"2015-12-31", endDate=u"2016-12-31",
                                         field="secID,tradeDate,closePrice", isOpen="1", pandas="1", secID=universe)
    close_prices = close_prices.rename(index=str, columns={"tradeDate": "payCashDate"})
    joined_list = close_prices.merge(fh, how='inner')
    joined_list['pay_cash_ratio'] = joined_list.perCashDiv / joined_list.closePrice
    print('#####CashDiv list sort#######')
    print(joined_list.sort(columns='pay_cash_ratio', ascending=False))


ROESelect('20170101')