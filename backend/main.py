import pandas as pd
import numpy as np
import akshare as ak
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind



# 加载 H5 文件中的股票数据
def load_stock_data(h5_file, start_date, end_date):
    return pd.HDFStore('all_stock_data.h5', mode='r')

# 获取上证指数数据


# 对齐股票数据和上证指数
def align_data(stock_data, sh_index):
    stock_data = stock_data.rename(columns={'stock_date': 'date'})
    aligned_data = pd.merge(stock_data, sh_index, on='date', how='inner')
    return aligned_data

# 统计分析
def perform_analysis(aligned_data):
    results = {}
    # 股票和上证指数的平均对数收益率
    avg_stock_return = aligned_data['log_return_x'].mean()
    avg_sh_return = aligned_data['log_return_y'].mean()
    results['avg_stock_return'] = avg_stock_return
    results['avg_sh_return'] = avg_sh_return

    # 股票收益率分布与上证指数分布的 t 检验
    t_stat, p_value = ttest_ind(aligned_data['log_return_x'], aligned_data['log_return_y'], equal_var=False)
    results['t_statistic'] = t_stat
    results['p_value'] = p_value

    # 股票跑赢上证指数的概率
    aligned_data['outperform'] = aligned_data['log_return_x'] > aligned_data['log_return_y']
    outperform_prob = aligned_data['outperform'].mean()
    results['outperform_probability'] = outperform_prob

    # 波动率分析
    stock_volatility = aligned_data['log_return_x'].std()
    sh_volatility = aligned_data['log_return_y'].std()
    results['stock_volatility'] = stock_volatility
    results['sh_volatility'] = sh_volatility

    # 最大回撤计算（股票和上证指数）
    aligned_data['stock_cum_return'] = (1 + aligned_data['log_return_x']).cumprod()
    aligned_data['sh_cum_return'] = (1 + aligned_data['log_return_y']).cumprod()
    stock_max_drawdown = (aligned_data['stock_cum_return'] / aligned_data['stock_cum_return'].cummax() - 1).min()
    sh_max_drawdown = (aligned_data['sh_cum_return'] / aligned_data['sh_cum_return'].cummax() - 1).min()
    results['stock_max_drawdown'] = stock_max_drawdown
    results['sh_max_drawdown'] = sh_max_drawdown

    return results, aligned_data

# 数据可视化
def visualize_results(aligned_data):
    # 累计收益率曲线
    plt.figure(figsize=(12, 6))
    plt.plot(aligned_data['date'], aligned_data['stock_cum_return'], label='Stock Cumulative Return')
    plt.plot(aligned_data['date'], aligned_data['sh_cum_return'], label='Shanghai Index Cumulative Return')
    plt.legend()
    plt.title('Cumulative Returns')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.grid()
    plt.show()

    # 对数收益率分布
    plt.figure(figsize=(12, 6))
    plt.hist(aligned_data['log_return_x'], bins=50, alpha=0.5, label='Stock Log Returns')
    plt.hist(aligned_data['log_return_y'], bins=50, alpha=0.5, label='Shanghai Index Log Returns')
    plt.legend()
    plt.title('Log Return Distribution')
    plt.xlabel('Log Return')
    plt.ylabel('Frequency')
    plt.grid()
    plt.show()

# 主函数
def main():
    # 参数设置
    h5_file = 'stock_data.h5'  # H5 文件路径
    start_date = '2022-01-01'
    end_date = '2023-01-01'

    # 加载数据
    stock_data = load_stock_data(h5_file, start_date, end_date)
    sh_index = get_shanghai_index(start_date, end_date)

    # 数据对齐
    aligned_data = align_data(stock_data, sh_index)

    # 统计分析
    results, aligned_data = perform_analysis(aligned_data)

    # 打印结果
    print("统计分析结果：")
    for key, value in results.items():
        print(f"{key}: {value}")

    # 数据可视化
    visualize_results(aligned_data)

if __name__ == "__main__":
    main()
