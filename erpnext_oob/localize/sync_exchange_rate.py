import frappe
from frappe.utils import flt
import requests as re
from bs4 import BeautifulSoup


currency_map = {
    '印度卢比':'INR',
    '瑞士法郎':'CHF',
    '日元':'JPY',
    '澳大利亚元':'AUD',
    '阿联酋迪拉姆':'AED',
    '欧元':'EUR',
    '英镑':'GBP',
    '美元':'USD',
    '港币':'HKD',
    '新西兰元':'NZD',
    '新台币':'TWD',
    '加拿大元':'CAD',
    '新加坡元':'SGD',
    '韩国元':'KRW',
    '澳门元':'MOP',
    '泰国铢':'THB',
    '瑞典克朗':'SEK',
    '沙特里亚尔':'SAR',
    '卢布':'RUB',
    '菲律宾比索':'PHP',
    '丹麦克朗':'DKK',
    '土耳其里拉':'TRY',
    '南非兰特':'ZAR',
    '印尼卢比':'IDR',
    '林吉特':'MYR',
    '挪威克朗':'NOK',
    '巴西里亚尔':'BRL'
}


def get_exchange_rate():
    """来源自https://gitee.com/link?target=https%3A%2F%2Fwww.jb51.net%2Farticle%2F226638.htm"""
    url = "https://www.bankofchina.com/sourcedb/whpj/"
    web=re.get(url)
    web.encoding=web.apparent_encoding
    #BeautifulSoup将字节流转换为utf-8编码
    bs_obj=BeautifulSoup(web.text,'lxml')
    #查找数据所在表格
    table=bs_obj.find_all('table')[1]
    #print(table)
    dataAll=[]
    for all_tr in table.find_all('tr'):#找到所有tr,返回一个列表
        all_th=all_tr.find_all('th')
        #print(all_th)
        all_td=all_tr.find_all('td')
        #print(all_td)
        if len(all_th)>0:
            dataRow=[]
            for item in all_th:
                dataRow.append(item.text)
            dataAll.extend([dataRow])
        if len(all_td)>0:
            dataRow=[]
            for item in all_td:
                dataRow.append(item.text)
            dataAll.extend([dataRow])
    return dataAll

@frappe.whitelist()
def sync_exchange_rate():
    exchange_rate_list = get_exchange_rate()
    if not exchange_rate_list: return
    active_currencies = frappe.get_all('Currency',filters={'enabled':1}, pluck='name')
    for row in exchange_rate_list[1:]:
        currency_name = row[0]
        buying_rate = flt(row[5]) / 100         #公布的汇率是每100外币兑人民币，第五列中行折算价
        publish_date = row[-2][:10]             #日期数据带时分秒需截取
        currency_code = currency_map.get(currency_name)
        #更新需满足3个条件，货币已定义且已激活，有汇率数据
        if currency_code and currency_code in active_currencies and buying_rate:
            doc_dict = frappe._dict({
                'date': publish_date,
                'from_currency': currency_code,
                'to_currency': 'CNY',
                'for_buying':1,
                'for_selling':1
            })
            doc = None
            try:
                doc = frappe.get_last_doc("Currency Exchange", doc_dict)
            except:
                pass
            #如果记录已存在，就更新，否则新增记录    
            if doc:
                doc.exchange_rate = buying_rate
                doc.save()
                print('currency exchange rate updated Okay')
            else:
                doc_dict.doctype = "Currency Exchange"
                doc_dict.exchange_rate = buying_rate
                frappe.get_doc(doc_dict).insert(ignore_permissions = True)
                print('currency exchange rate inserted Okay')
