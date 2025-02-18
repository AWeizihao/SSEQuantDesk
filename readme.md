# SSEQuantDesk 股票市场量化分析工具

本项目是一个基于 Python 和 HTML/JS 的股票市场统计分析平台，能实现投资组合分析，并提供（简易的）量化回测。

本项目是桌面应用，后端基于 Flask（waitress WSGI 服务器）和 python。数据来自开源 python 库 akshare。前端采用web前端，使用简单的html和javacript实现交互和可视化。


## ToDo List 完成度

+ 容器化：使用 Docker 容器化部署，更方便在各种操作系统环境下进行快速安装与更新
+ 风险控制模块
+ 利用定时任务（如 `crontab` 或诸如 Airflow/Prefect 等调度系统）实现自动抓取、更新数据，为回测提供更加实时的行情信息。

---

## 安装与运行

1. **克隆项目到本地**

   ```bash
   git clone https://github.com/AWeizihao/SSEQuantDesk.git
   cd SSEQuantDesk
   ```

2. **依赖库**
   本项目依赖库清单：

   - 基础库：numpy, pandas, matplotlib, io, time, scipy, base64, logging
   - seaborn
     美化可视化图表
   - statsmodels
   - flask
     一个轻量级的 Python Web 框架。简单、灵活，易于扩展。Flask 基于 WSGI（Web Server Gateway Interface） 和 Werkzeug 库，主要工作流程为监听http请求，随后解析并传递给视图函数，并将结果返回。
   - waitress
     适用于生产环境的WSGI服务器
   - akshare
     一个伟大的开源项目（！！），提供任意时间的资本市场数据。

3. **启动项目**
  在terminal里输入：

   ```bash
   flask run
   ```

  即可启动。

  或（如果是vscode）使用 code runner 等插件运行 app.py 。务必使编辑器打开整个文件夹。

  启动后，浏览器内访问默认端口 `http://127.0.0.1:5000`，即可看到项目首页。


## 功能介绍

目前功能包含如下统计分析：

+ 整体分析：
  + 波动：标准差
  + 平均收益率
  + 统计分布，包括峰度和偏度。峰度
  + 通过 `stats_summary` 可以查看个股和上证指数的  **平均收益率、波动率、偏度和峰度** ，判断个股收益情况。偏度（Skewness）和峰度（Kurtosis）可以帮助分析收益率分布是否偏离正态分布。
+ 累计收益：

  * **累积收益率曲线** 直观展示了个股与上证指数的长期表现差异。
  * `np.exp(log_return.cumsum()) - 1` 计算 **连续复利的累积收益**
+ * **线性相关性**
  * 计算个股与上证指数的  **Pearson 相关系数** ，并绘制  **散点图与回归线** 。
  * 相关性接近 1，说明个股与指数走势高度一致；接近 0，说明无明显关系。

* **波动聚集性分析**

  * 计算 **收益率的绝对值** (衡量波动率) 的自相关性。
  * 如果波动率在时间上有持续性（即波动聚集现象），则市场可能存在  **GARCH 效应** 。
  * 
* **滞后性分析**

  * 自相关函数（ACF）和偏自相关函数（PACF）用于判断个股收益率是否受自身历史数据影响。
  * 若存在显著的自相关性，可能暗示  **收益序列有可预测性** 。
* **其他关系探索**

  * **滚动相关性** ：观察相关性是否随时间变化，可能揭示市场结构变化。
  * **β值计算** ：衡量个股相对于市场的系统性风险。


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
* `outstanding_share`
* `turnover`
* `log_return`：对数收益率（`log(close_t / close_t-1)`）。
* `stock_code`：股票代码。


## 许可证
本项目采用 **MIT** 许可证，详细内容见 LICENSE 文件。

---

感谢您对 SSEQuantDesk 项目的关注与支持！这最初只是一个个人用于统计分析上证股票的玩具项目。如果在使用过程中有任何疑问或想法，欢迎在 Issue 区进行探讨，或联系邮箱 `aweizihao@outlook.com`，共同完善该项目，让更多人受益于量化分析与自动化交易的乐趣与价值。


