import akshare as ak
import numpy as np
import pandas as pd
import time

#date,
# 获取上交所和深交所所有股票列表
stock_list = ak.stock_info_sh_name_code()
stock_codes = stock_list['证券代码'].tolist()
stock_names = stock_list['证券简称'].tolist()

# 设置下载时间范围
start_date = "20200101"
end_date = "20240205"

# 初始化 HDFStore，用于存储所有股票数据
import os
if os.path.exists('./Database/sh_stock_data.h5'):
    os.remove('./Database/sh_stock_data.h5')
store = pd.HDFStore('./Database/sh_stock_data.h5', mode='w')

# 遍历股票代码列表，下载数据
for code in stock_codes:
    try:
        # 下载股票日线数据
        stock_df = ak.stock_zh_a_daily(symbol="sh" + code, start_date=start_date, end_date=end_date, adjust="qfq")

        # 计算对数收益率
        stock_df['log_return'] = np.log(stock_df['close'] / stock_df['close'].shift(1))

        # 添加股票代码列
        stock_df['stock_code'] = code
        
        # 重置索引，将日期列设置为普通列
        stock_df.reset_index(inplace=True)
        stock_df.rename(columns={'index': 'stock_date'}, inplace=True)

        stock_df['stock_date'] = pd.to_datetime(stock_df['date'])

        stock_df=stock_df.drop('date',axis=1)

        # 将数据追加到 HDFStore 中的同一个表中
        store.append('stock_date', stock_df, format='table', data_columns=['stock_code', 'stock_date'])

        print(f"{code} 数据下载并保存成功")
    except Exception as e:
        print(f"{code} 数据下载失败: {e}")
    time.sleep(0.1)

store.close()
#index        date   open   high    low  close     volume       amount  outstanding_share  turnover  log_return stock_code
     