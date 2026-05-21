import requests
import json
import os
import xml.etree.ElementTree as ET

def get_full_data():
    # 使用通用的 Atom Feed，它包含所有类型的申报
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=&company=&dateb=&owner=include&count=40&output=atom"
    headers = {"User-Agent": "Mozilla/5.0 (MyInsiderMonitor/1.0; xinghang7@gmail.com)"}
    
    response = requests.get(url, headers=headers)
    root = ET.fromstring(response.content)
    result = []

    # 遍历所有申报项，不再做复杂的金额筛选，先确保能抓到数据
    for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        updated = entry.find('{http://www.w3.org/2005/Atom}updated').text
        
        result.append({
            "symbol": "SEC",
            "name": title,
            "title": "申报文件",
            "action": "Disclosure",
            "totalValue": 1000, # 填个数字让前端能显示
            "date": updated,
            "historyCount": 1
        })

    # 保存
    if not os.path.exists('data'):
        os.makedirs('data')
    with open('data/insider.json', 'w') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    get_full_data()
