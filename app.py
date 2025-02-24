import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 关闭GUI
plt.switch_backend('Agg')
from flask import Flask, render_template, request, jsonify
import sys
import io as io
import os
import base64 as base64
import time
import logging
import All_methods.file_operations as fo
import All_methods.fi_statistics as st

app = Flask(__name__)


server = os.getenv("SERVER_SOFTWARE", "Unknown Server")
print(f"当前服务器: {server}")


@app.route('/')
def home():
    return render_template('base.html', content_template="index.html")

# 记录日志
logging.basicConfig(filename="performance.log", level=logging.INFO)

@app.before_request
def start_timer():
    request.start_time = time.perf_counter()

@app.after_request
def log_request_time(response):
    elapsed_time = time.perf_counter() - request.start_time
    response.headers["X-Response-Time"] = str(elapsed_time)
    log_message = f"Request {request.method} {request.path} took {elapsed_time:.6f} seconds"
    print(log_message)
    logging.info(log_message)  # 存入日志
    return response

@app.route('/stock_sh',methods=['POST'])
def Stock_SH():
    try:
        # 从请求中获取 JSON 数据
        request_data = request.get_json()
        stock = request_data.get("stock1", "Stock1")  # 获取股票名称
        max_lag = int(request_data.get("max_lag", 10))  # 获取最大滞后阶数
        start_date = request_data.get("start_date", "")
        end_date = request_data.get("end_date", "")

        print("1",start_date,end_date)

        if not start_date or not end_date :
            return jsonify({"error": "缺少开始日期或结束日期，或开始日期晚于结束日期"}), 400

        sh_index_data = fo.get_shanghai_index(start_date, end_date,'log_return')# 读取上证指数
        stock_data=fo.load_stock_data(stock,start_date, end_date)
        data=fo.merge_stocks(sh_index_data, stock_data)
        if data.empty:
            raise ValueError("合并后的数据为空，可能是上证指数或股票数据缺失！")

        # 生成 ACF/PACF 图
        image_base64 = st.lag_effect(data, stock, '000001.ss', max_lag)

        # 计算相关性并生成散点图
        correlation, image_cor = st.cor(data, stock, '000001.ss')

        mean1,vol1,skew1,kurt1=st.statistic_overview(stock_data)
        mean2,vol2,skew2,kurt2=st.statistic_overview(sh_index_data)

        # 返回 JSON 数据
        return jsonify({
            "img_lag_effect": image_base64,
            "text1": f"ACF（收益率自相关）和 PACF（收益率偏自相关） 图已生成，最大滞后阶数为 {max_lag}。",
            'beta':st.beta(data),
            'img_rolling_correlation':st.rolling_cor(data,stock,"000001.ss"),
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
    app.run(debug=True,threaded=True)
