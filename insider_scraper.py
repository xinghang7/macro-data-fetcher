import requests
import json
import os
import xml.etree.ElementTree as ET

def get_full_data():
    # 扩展 SEC RSS 获取范围 (合并多种申报)
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=&company=&dateb=&owner=include&count=40&output=atom"
    headers = {"User-Agent": "Mozilla/5.0 (MyInsiderMonitor/1.0; xinghang7@gmail.com)"}
    
    response = requests.get(url, headers=headers)
    root = ET.fromstring(response.content)
    result = []

    # 监控的目标表单
    targets = ['Form 3', 'Form 4', 'SC 13D', 'SC 13G']

    for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        if any(t in title for t in targets):
            # 简化提取流程，先确保我们拿到了所有这些类型的记录
            result.append({
                "symbol": title.split('(')[-1].replace(')', ''), # 尝试从标题提取代号
                "name": title.split(' - ')[0],
                "title": "Insider/Major Shareholder",
                "action": "Disclosure",
                "totalValue": 0, # 此处为占位，后续可深入解析 XML
                "date": entry.find('{http://www.w3.org/2005/Atom}updated').text,
                "historyCount": 1
            })

    # 保存文件
    if not os.path.exists('data'):
        os.makedirs('data')
    with open('data/insider.json', 'w') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    get_full_data()
