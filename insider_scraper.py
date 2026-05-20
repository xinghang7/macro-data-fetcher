import pandas as pd
import json
import os
import requests
from io import StringIO

# 1. 设置伪装请求头，模拟真实浏览器访问
url = "http://openinsider.com/feed/?q=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

# 2. 发起请求并读取 CSV
response = requests.get(url, headers=headers)
if response.status_code == 200:
    df = pd.read_csv(StringIO(response.text))
else:
    print(f"请求失败，状态码: {response.status_code}")
    exit(1) # 如果下载失败，直接停止运行

# 3. 筛选重要交易 (CEO/CFO, 金额 > 50万)
data = df[(df['Officer Title'].str.contains('CEO|CFO', na=False)) & 
          (df['Value ($)'] > 500000)].copy()

# 4. 整理格式
result = []
for _, row in data.iterrows():
    result.append({
        "symbol": row['Ticker'],
        "name": row['Reporter Name'],
        "title": row['Officer Title'],
        "action": 'Buy' if 'Purchase' in row['Transaction Type'] else 'Sell',
        "totalValue": row['Value ($)'],
        "date": row['Filing Date'],
        "historyCount": 1
    })

# 5. 保存到 GitHub 仓库内的文件
if not os.path.exists('data'):
    os.makedirs('data')
with open('data/insider.json', 'w') as f:
    json.dump(result, f, indent=2)
