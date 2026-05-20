import os
import requests
import json
from datetime import datetime

# 微信鉴权配置
APPID = os.environ.get('WECHAT_APPID')
SECRET = os.environ.get('WECHAT_SECRET')
ENV_ID = os.environ.get('WECHAT_ENV_ID')

def get_fred_data(series_id):
    """最稳妥的直接抓取方式，不依赖第三方库"""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    # 设置一个标准的浏览器UA，防止被拦截
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=20)
    lines = response.text.strip().split('\n')
    # 取最后一行有效数据
    last_row = lines[-1].split(',')
    return {'date': last_row[0], 'value': float(last_row[1])}

def update_db(data):
    # 1. 换取 Token
    token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={SECRET}"
    token = requests.get(token_url).json()['access_token']
    
    # 2. 写入数据库
    url = f"https://api.weixin.qq.com/tcb/databaseupdate?access_token={token}"
    # 注意：我们这里存入日期和两个利率值
    query = f"""
    db.collection("liquidity").doc("liquidity_latest").set({{
        data: {{
            sofr: {data['sofr']},
            iorb: {data['iorb']},
            date: "{data['date']}",
            updateTime: db.serverDate()
        }}
    }})
    """
    requests.post(url, json={"env": ENV_ID, "query": query})

if __name__ == "__main__":
    sofr = get_fred_data('SOFR')
    iorb = get_fred_data('IORB')
    update_db({'sofr': sofr['value'], 'iorb': iorb['value'], 'date': sofr['date']})
    print(f"✅ 数据同步完成: SOFR={sofr['value']}, IORB={iorb['value']}")
