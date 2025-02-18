import pandas as pd
import numpy as np
import akshare as ak
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 服务器模式
import seaborn as sns
from scipy.stats import skew, kurtosis
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from flask import Flask, render_template, request, jsonify
import io as io
import base64 as base64




app = Flask(__name__)

@app.route('/')
def home():
    return render_template('base.html', content_template="index.html")

# HDF5 文件
file_path = '.\Database\sh_stock_data.h5'

start_date = '2023-01-01'
end_date = '2023-12-31'

sns.set_style("whitegrid")


def load_stock_data(stock_code, start_date, end_date):
    """
    读取 HDF5 文件中的股票数据，并返回包含日期和 log_return 的 DataFrame
    """
    data = pd.read_hdf(
        file_path,
        key='stock_date',
        where=f"stock_code='{stock_code}' & stock_date>='{start_date}' & stock_date<='{end_date}'"
    )
    data = data[['stock_date', 'log_return']].set_index('stock_date')
    data.rename(columns={'log_return': f'log_return_{stock_code}'}, inplace=True)
    return data

def merge_stocks(data1, data2):
    """
    合并两个股票的数据，按日期对齐
    """
    merged_data = data1.join(data2, how='inner')  # 仅保留共同日期的数据
    return merged_data

def get_shanghai_index(start_date, end_date,info):# 获取上证数据
    sh_index = ak.stock_zh_index_daily(symbol="sh000001")  # 上证指数代码
    sh_index['date'] = pd.to_datetime(sh_index['date'])  # 转换日期
    sh_index = sh_index[(sh_index['date'] >= start_date) & (sh_index['date'] <= end_date)]
    sh_index['log_return'] = np.log(sh_index['close'] / sh_index['close'].shift(1))  # 计算对数收益率
    
    return sh_index[['date', f"{info}"]].dropna().set_index('date')

def statistic_overview(data):
    #data是一个pandas数据库DataFrame，要求有以下结构：以日期为索引，任意列数，不同列数据属性一致。
    # 计算统计特征，包括平均收益率、标准差、偏度、峰度
    if data.empty:
        raise ValueError(f"股票统计 {stock_code} 在 {start_date} ~ {end_date} 无数据！")
    return  data.mean(),data.std(),data.apply(skew),data.apply(kurtosis)

def cumulative_return_visible(data):
    #data是一个包含列名为'stock_log_return'和'sh_index_log_return'的两列数据表。
    # 计算累积收益率
    data['stock_cum_return'] = np.exp(data['stock_log_return'].cumsum()) - 1
    data['sh_index_cum_return'] = np.exp(data['sh_index_log_return'].cumsum()) - 1

    # 绘制累积收益率曲线
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['stock_cum_return'], label=f'Stock  Cumulative Return', color='blue')
    plt.plot(data.index, data['sh_index_cum_return'], label='Shanghai Index Cumulative Return', color='red')

    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.title('Cumulative Return Comparison')
    plt.legend()
    plt.grid(True)
    plt.show()

def cor(data, stock1, stock2, info='对数收益率'):
    """
    计算相关性，并绘制散点图。info 为数据描述字符串
    """
    correlation = data.corr().iloc[0, 1]
    
    # 创建 Matplotlib 图
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(x=data.iloc[:, 0], y=data.iloc[:, 1], scatter_kws={'alpha': 0.5}, ax=ax)
    ax.set_xlabel(f"{stock1} {info}")
    ax.set_ylabel(f"{stock2} {info}")
    ax.set_title(f"{stock1} vs {stock2} {info}相关性")

    # 将图像保存到内存
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    plt.close(fig)  # 关闭图形，释放内存

    return correlation, img_base64


def volatility_clustering(data, stock1, stock2, lags=20):
    """
    进行波动聚集性分析 (收益率绝对值的自相关性)
    """
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plot_acf(np.abs(data.iloc[:, 0]).dropna(), lags=lags, title=f"{stock1} 波动率自相关")

    plt.subplot(1, 2, 2)
    plot_acf(np.abs(data.iloc[:, 1]).dropna(), lags=lags, title=f"{stock2} 波动率自相关")

    plt.show()

def lag_effect(data, stock1, stock2, max_lag=10):
    """
    计算两个股票的收益率滞后效应，并返回 ACF/PACF 图的 Base64 编码
    """

    # 创建图像
    fig, axes = plt.subplots(2, 2, figsize=(12, 6))

    # 绘制 ACF 和 PACF 图
    plot_acf(data.iloc[:, 0].dropna(), lags=max_lag, ax=axes[0, 0])
    axes[0, 0].set_title(f"{stock1} 收益率自相关 (ACF)")

    plot_pacf(data.iloc[:, 0].dropna(), lags=max_lag, ax=axes[0, 1])
    axes[0, 1].set_title(f"{stock1} 收益率偏自相关 (PACF)")

    plot_acf(data.iloc[:, 1].dropna(), lags=max_lag, ax=axes[1, 0])
    axes[1, 0].set_title(f"{stock2} 收益率自相关 (ACF)")

    plot_pacf(data.iloc[:, 1].dropna(), lags=max_lag, ax=axes[1, 1])
    axes[1, 1].set_title(f"{stock2} 收益率偏自相关 (PACF)")

    plt.tight_layout()

    # 将图像保存到内存中并转换为 Base64 编码
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    plt.close(fig)  # 关闭 Matplotlib 图形，释放内存

    # 返回 Base64 编码的图片
    return img_base64


def rolling_cor(data, stock1, stock2, window_size=30):
    """
    计算两个股票的滚动相关性，并返回相关性图的 Base64 编码。默认滚动窗口30 days
    """
    data['rolling_corr'] = data.iloc[:, 0].rolling(window=window_size).corr(data.iloc[:, 1])

    # 绘制滚动相关性图
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data.index, data['rolling_corr'], label=f"Rolling Correlation ({window_size}-day)", color="purple")
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.6)
    ax.set_xlabel("Date")
    ax.set_ylabel("Correlation")
    ax.set_title(f"{stock1} vs {stock2} 滚动相关性")
    ax.legend()

    # 将图像保存到内存
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    plt.close(fig)  # 关闭图形，释放内存

    return img_base64


def beta(data):
    # 计算β值:{stock1} 对 {stock2} 的 Beta 值
    X = sm.add_constant(data.iloc[:, 1].dropna())  # 添加截距项
    y = data.iloc[:, 0].dropna()
    model = sm.OLS(y, X).fit()
    beta = model.params.iloc[1]

    return f"stock1 对 stock2 的 Beta 值: {beta:.4f}"

@app.route('/stock_sh',methods=['POST'])
def Stock_SH():
    try:
        # 从请求中获取 JSON 数据
        request_data = request.get_json()
        stock = request_data.get("stock1", "Stock1")  # 获取股票名称
        max_lag = int(request_data.get("max_lag", 10))  # 获取最大滞后阶数

        sh_index_data = get_shanghai_index(start_date, end_date,'log_return')# 读取上证指数
        stock_data=load_stock_data(stock,start_date, end_date)
        data=merge_stocks(sh_index_data, stock_data)
        if data.empty:
            raise ValueError("合并后的数据为空，可能是上证指数或股票数据缺失！")

        # 生成 ACF/PACF 图
        image_base64 = lag_effect(data, stock, '000001.ss', max_lag)

        # 计算相关性并生成散点图
        correlation, image_cor = cor(data, stock, '000001.ss')

        mean1,vol1,skew1,kurt1=statistic_overview(stock_data)
        mean2,vol2,skew2,kurt2=statistic_overview(sh_index_data)

        # 返回 JSON 数据
        return jsonify({
            "img_lag_effect": image_base64,
            "text1": f"ACF（收益率自相关）和 PACF（收益率偏自相关） 图已生成，最大滞后阶数为 {max_lag}。",
            'beta':beta(data),
            'img_rolling_correlation':rolling_cor(data,stock,"000001.ss"),
            'text2':f"滚动相关图已生成",
            'img_cor':image_cor,
            'correlation':f"股票 {stock} 与 000001.ss 的收益率相关性: {correlation:.8f}",
            '股票平均收益率Mean Return': f"{mean1.item()}",
            '上证平均收益率Mean Return':f"{mean2.item():4f}",
            '股票标准差Volatility (Std Dev)':f"{vol1.item():8f}", 
            '上证标准差Volatility (Std Dev)':f"{vol2.item():8f}",
            '股票偏度Skewness':f"{skew1.item():4f}",
            '上证偏度Skewness':f"{skew2.item():4f}",
            '股票峰度Kurtosis':f"{kurt1.item():4f}",
            '上证峰度Kurtosis':f"{kurt2.item():4f}"
        })

    except Exception as e:
        return jsonify({"error": str(e)})



@app.route('/analysis')
def analysis():
    return render_template('base.html', content_template="analysis.html")

@app.route('/prediction')
def prediction():
    return render_template('base.html', content_template="prediction.html")

@app.route('/trend')
def trend():
    return render_template('base.html', content_template="trend.html")


if __name__ == "__main__":
    app.run(debug=True)
