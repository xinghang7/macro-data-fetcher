import requests
import os
from datetime import datetime

# ================= 配置区 =================
# 这里直接从 GitHub 极其安全的 Secrets 里读取你的微信密钥，绝对不会泄露
APPID = os.environ.get('WECHAT_APPID')
SECRET = os.environ.get('WECHAT_SECRET')
ENV_ID = os.environ.get('WECHAT_ENV_ID')
# =========================================

def get_official_fred_data(series_id):
    """直接从美联储官方获取最权威数据（GitHub在美国机房，直连无压力）"""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    res = requests.get(url, headers=headers, timeout=10)
    lines = res.text.strip().split('\n')
    
    # 倒序查找最新一天的有效数值
    for i in range(len(lines)-1, 0, -1):
        row = lines[i].split(',')
        try:
            val = float(row[1])
            return {'date': row[0], 'value': val}
        except ValueError:
            continue
    raise Exception(f"未找到 {series_id} 的有效数据")

def update_wechat_database(sofr_data, iorb_data):
    """调用微信官方 HTTP API 将数据强行写入云数据库"""
    # 1. 用 AppID 和 Secret 换取 Access Token
    token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={SECRET}"
    token_res = requests.get(token_url).json()
    access_token = token_res.get('access_token')

    if not access_token:
        print("❌ 获取微信鉴权 Token 失败:", token_res)
        return

    # 2. 组装数据库更新指令 
    db_url = f"https://api.weixin.qq.com/tcb/databaseupdate?access_token={access_token}"
    query = f"""
    db.collection("liquidity").doc("liquidity_latest").update({{
        data: {{
            sofr: {sofr_data['value']},
            iorb: {iorb_data['value']},
            sofrDate: "{sofr_data['date']}",
            iorbDate: "{iorb_data['date']}",
            updateTime: db.serverDate()
        }}
    }})
    """
    
    payload = {
        "env": ENV_ID,
        "query": query
    }
    
    # 3. 发送更新请求
    res = requests.post(db_url, json=payload).json()
    if res.get('errcode') == 0:
        print("✅ 微信云数据库更新成功！")
        print(f"写入详情 -> SOFR: {sofr_data['value']} ({sofr_data['date']}), IORB: {iorb_data['value']} ({iorb_data['date']})")
    else:
        print("❌ 写入数据库失败:", res)

if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行宏观流动性数据抓取...")
    try:
        sofr = get_official_fred_data('SOFR')
        iorb = get_official_fred_data('IORB')
        update_wechat_database(sofr, iorb)
    except Exception as e:
        print("❌ 执行过程中发生错误:", e)