from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
ts = TimeSeries(key='YOUR_API_KEY', output_format='pandas')
data, meta_data = ts.get_daily(
    symbol='PETR4.SAO', outputsize='compact')
print(data)
data['4. close'].plot()
plt.title('Intraday TimeSeries Google')
plt.show()
