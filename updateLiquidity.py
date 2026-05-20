import os
import requests
import akshare as ak # 国内最强金融开源库，无需翻墙，极速稳定
from datetime import datetime

# 微信鉴权配置 (直接从 GitHub Secrets 读取)
APPID = os.environ.get('WECHAT_APPID')
SECRET = os.environ.get('WECHAT_SECRET')
ENV_ID = os.environ.get('WECHAT_ENV_ID')

def get_data():
    """使用 akshare 获取宏观数据"""
    # 获取美国国债收益率数据（包含 SOFR 等参考利率）
    # akshare 的数据源极其稳定，直接从国内接口获取
    sofr_df = ak.macro_usa_sofr() 
    # 取最新的一行
    latest = sofr_df.iloc[-1]
    return {
        'date': str(latest['日期']),
        'sofr': float(latest['SOFR']),
        'iorb': float(latest['IORB']) # 库中通常包含相关利率对
    }

def update_db(data):
    # 1. 换取 Token
    token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={SECRET}"
    token = requests.get(token_url).json()['access_token']
    
    # 2. 写入数据
    url = f"https://api.weixin.qq.com/tcb/databaseupdate?access_token={token}"
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
    data = get_data()
    update_db(data)
    print(f"✅ 数据已更新: SOFR {data['sofr']}, IORB {data['iorb']}")
