import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def get_stock_data_akshare(symbol, start_date, end_date):
    """
    使用AkShare获取股票数据
    """
    try:
        # AkShare的代码格式：上海股票用sh，深圳股票用sz
        if symbol.endswith('.SS'):
            ak_symbol = symbol.replace('.SS', '')
            market = "sh"
        elif symbol.endswith('.SZ'):
            ak_symbol = symbol.replace('.SZ', '')
            market = "sz"
        else:
            ak_symbol = symbol
            market = "sh"  # 默认上海

        # 获取股票数据
        stock_data = ak.stock_zh_a_hist(symbol=ak_symbol, period="daily",
                                        start_date=start_date, end_date=end_date,
                                        adjust="hfq")

        if stock_data.empty:
            print(f"AkShare未找到 {symbol} 的数据")
            return pd.DataFrame()

        # 重命名列以保持一致性
        stock_data.rename(columns={
            '日期': 'Date',
            '开盘': 'Open',
            '收盘': 'Close',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume'
        }, inplace=True)

        # 设置日期为索引
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])
        stock_data.set_index('Date', inplace=True)

        print(f"成功获取 {symbol} 的数据，共 {len(stock_data)} 条记录")
        return stock_data

    except Exception as e:
        print(f"获取 {symbol} 数据时出错: {e}")
        return pd.DataFrame()


def main():
    print("=== 量化交易数据获取程序（使用AkShare）===")

    # 股票代码和日期设置（使用AkShare格式）
    symbols = [
        "600519",  # 贵州茅台
        "000858",  # 五粮液
        "000001",  # 平安银行
    ]

    start_date = "20220101"  # AkShare需要YYYYMMDD格式
    end_date = "20230101"

    # 获取数据
    successful_data = {}

    for symbol in symbols:
        print(f"\n正在获取股票: {symbol}")
        data = get_stock_data_akshare(symbol, start_date, end_date)

        if not data.empty:
            successful_data[symbol] = data
            print(f"{symbol} 数据预览:")
            print(data.head())
        else:
            print(f"未能获取 {symbol} 的数据")

        # 短暂延迟避免请求过快
        import time
        time.sleep(1)

    # 结果显示和分析
    print(f"\n=== 数据获取结果汇总 ===")
    print(f"成功获取 {len(successful_data)} 只股票的数据")

    if successful_data:
        print("成功获取数据的股票:")
        for symbol in successful_data.keys():
            data = successful_data[symbol]
            close_prices = data['Close']
            print(f"  - {symbol}: {len(data)} 个交易日，收盘价范围 {close_prices.min():.2f} - {close_prices.max():.2f}")

        # 基本分析
        print("\n=== 简单的数据分析 ===")
        for symbol, data in successful_data.items():
            close_prices = data['Close']
            returns = close_prices.pct_change().dropna()

            print(f"\n{symbol} 分析结果:")
            print(f"  收盘价均值: {close_prices.mean():.2f}")
            print(f"  收盘价标准差: {close_prices.std():.2f}")
            print(f"  期间收益率: {((close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0] * 100):.2f}%")
            print(f"  日均收益率: {returns.mean() * 100:.4f}%")
            print(f"  收益波动率: {returns.std() * 100:.4f}%")

        # 绘制价格走势图
        try:
            plt.figure(figsize=(14, 8))

            # 创建子图
            plt.subplot(2, 1, 1)
            for symbol, data in successful_data.items():
                # 归一化价格（以起始日为1）
                normalized_price = data['Close'] / data['Close'].iloc[0]
                plt.plot(data.index, normalized_price, label=symbol, linewidth=2)

            plt.title('股票价格走势对比（归一化）')
            plt.xlabel('日期')
            plt.ylabel('归一化价格')
            plt.legend()
            plt.grid(True, alpha=0.3)

            # 绘制成交量
            plt.subplot(2, 1, 2)
            for symbol, data in successful_data.items():
                # 归一化成交量
                normalized_volume = data['Volume'] / data['Volume'].max()
                plt.plot(data.index, normalized_volume, label=f"{symbol}成交量", alpha=0.7)

            plt.title('成交量对比（归一化）')
            plt.xlabel('日期')
            plt.ylabel('归一化成交量')
            plt.legend()
            plt.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"绘图时出错: {e}")

    else:
        print("未能获取任何股票数据")
        print("\n建议:")
        print("1. 检查网络连接")
        print("2. 确认股票代码格式正确")
        print("3. 尝试更新AkShare: pip install akshare --upgrade")

    print("\n=== 程序执行完毕 ===")


if __name__ == "__main__":
    main()