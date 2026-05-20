import requests
import os
from datetime import datetime

# ================= 配置区 =================
APPID = os.environ.get('WECHAT_APPID')
SECRET = os.environ.get('WECHAT_SECRET')
ENV_ID = os.environ.get('WECHAT_ENV_ID')
# =========================================

def get_real_fred_data(series_id):
    """从FRED官方获取真实数据，直接请求"""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    # GitHub服务器在海外，直连官方非常快，不需要代理
    res = requests.get(url, headers=headers, timeout=15)
    lines = res.text.strip().split('\n')
    
    # 倒序找最新一行
    for i in range(len(lines)-1, 0, -1):
        row = lines[i].split(',')
        try:
            val = float(row[1])
            return {'date': row[0], 'value': val}
        except: continue
    raise Exception(f"未找到 {series_id} 数据")

def update_wechat_database(sofr, iorb):
    # 1. 换 Token
    token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={SECRET}"
    token = requests.get(token_url).json().get('access_token')
    
    # 2. 写入数据库
    db_url = f"https://api.weixin.qq.com/tcb/databaseupdate?access_token={token}"
    query = f"""
    db.collection("liquidity").doc("liquidity_latest").set({{
        data: {{
            sofr: {sofr['value']},
            iorb: {iorb['value']},
            sofrDate: "{sofr['date']}",
            iorbDate: "{iorb['date']}",
            updateTime: db.serverDate()
        }}
    }})
    """
    requests.post(db_url, json={"env": ENV_ID, "query": query})

if __name__ == "__main__":
    sofr = get_real_fred_data('SOFR')
    iorb = get_real_fred_data('IORB')
    update_wechat_database(sofr, iorb)
    print(f"✅ 更新成功: SOFR={sofr['value']}, IORB={iorb['value']}")
