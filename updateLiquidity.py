import os
import requests

APPID = os.environ.get('WECHAT_APPID')
SECRET = os.environ.get('WECHAT_SECRET')
ENV_ID = os.environ.get('WECHAT_ENV_ID')

def get_data_from_file():
    """直接读取仓库里的文本文件"""
    with open('data.txt', 'r') as f:
        content = f.read().strip().split(',')
        return {'sofr': float(content[0].strip()), 'iorb': float(content[1].strip())}

def update_db(data):
    token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={SECRET}"
    token = requests.get(token_url).json()['access_token']
    
    url = f"https://api.weixin.qq.com/tcb/databaseupdate?access_token={token}"
    query = f"""
    db.collection("liquidity").doc("liquidity_latest").set({{
        data: {{
            sofr: {data['sofr']},
            iorb: {data['iorb']},
            updateTime: db.serverDate()
        }}
    }})
    """
    requests.post(url, json={"env": ENV_ID, "query": query})

if __name__ == "__main__":
    data = get_data_from_file()
    update_db(data)
    print(f"✅ 同步成功: SOFR={data['sofr']}, IORB={data['iorb']}")
