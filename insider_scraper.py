import pandas as pd
import json
import os

# 1. 抓取数据
url = "http://openinsider.com/feed/?q=1"
df = pd.read_csv(url)

# 2. 筛选重要交易 (CEO/CFO, 金额 > 50万)
data = df[(df['Officer Title'].str.contains('CEO|CFO', na=False)) & 
          (df['Value ($)'] > 500000)].copy()

# 3. 整理成我们要的格式
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

# 4. 保存文件到 data 文件夹下
if not os.path.exists('data'):
    os.makedirs('data')
with open('data/insider.json', 'w') as f:
    json.dump(result, f, indent=2)
