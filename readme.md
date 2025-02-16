# 股票市场分析工具

按照下面的逻辑设计：

1. sjcl.py负责下载数据，放到sh_stock_data.h5中
2. main.py读取数据，截取一段时间，将每一只股票与上证指数相比较

## 数据库文件Database

HDF5 文件是通过 Pandas 的 `HDFStore` 类创建和管理的，数据被以表格式存储。数据存储在 HDF5 文件的 key 为 `'stock_date'` 的表中。使用了 `format='table'`，也就是表格式（Table Format），支持分块读写和查询操作。

存储的数据是一个 Pandas DataFrame，sjcl.py在拉取数据后，每次循环都会将新的股票数据（`stock_df`）追加到 `'stock_date'` 表中。下载完成的数据文件，以股票编码和日期为索引，包含列：

* `stock_date`：股票交易日期，数据类型为时间戳（datetime64）。
* `open`：开盘价。
* `close`：收盘价。
* `high`：最高价。
* `low`：最低价。
* `volume`：成交量。
* `amount`：成交金额。
* outstanding_share
* turnover
* `log_return`：对数收益率（`log(close_t / close_t-1)`）。
* `stock_code`：股票代码。

1. **`where` 参数的使用** :

* `where` 参数支持 SQL-like 的条件语句。
* 条件中的列必须是 `data_columns` 中的列（代码中已经将 `stock_date` 和 `stock_code` 设置为 `data_columns`）。

2. **性能优化** :

* 如果数据量非常大，建议使用 `chunksize` 参数分块读取。
* 例如，可以逐块处理大文件：

  ```python
  for chunk in pd.read_hdf(
    file_path,
    key='stock_date',
    where=f"stock_code='{stock_code}' & stock_date>='{start_date}' & stock_date<='{end_date}'",
    chunksize=1000):
    # 对每个块进行操作
    print(chunk[['stock_date', column_to_extract]])

  ```

## vssh.py的任务

1. 导入数据到pandas
2. 导入上证数据
3. 对比任意一支股票与上证

包含如下统计分析：

+ 整体分析：

  + 波动：标准差
  + 平均收益率
  + 统计分布，包括峰度和偏度。峰度
  + 通过 `stats_summary` 可以查看个股和上证指数的  **平均收益率、波动率、偏度和峰度** ，判断个股收益情况。偏度（Skewness）和峰度（Kurtosis）可以帮助分析收益率分布是否偏离正态分布。
+ 累计收益：

  * **累积收益率曲线** 直观展示了个股与上证指数的长期表现差异。
  * `np.exp(log_return.cumsum()) - 1` 计算 **连续复利的累积收益**
+  * **线性相关性**

    * 计算个股与上证指数的  **Pearson 相关系数** ，并绘制  **散点图与回归线** 。
    * 相关性接近 1，说明个股与指数走势高度一致；接近 0，说明无明显关系。
  * **波动聚集性分析**

    * 计算 **收益率的绝对值** (衡量波动率) 的自相关性。
    * 如果波动率在时间上有持续性（即波动聚集现象），则市场可能存在  **GARCH 效应** 。
  * **滞后性分析**

    * 自相关函数（ACF）和偏自相关函数（PACF）用于判断个股收益率是否受自身历史数据影响。
    * 若存在显著的自相关性，可能暗示  **收益序列有可预测性** 。
  * **其他关系探索**

    * **滚动相关性** ：观察相关性是否随时间变化，可能揭示市场结构变化。
    * **β值计算** ：衡量个股相对于市场的系统性风险。
