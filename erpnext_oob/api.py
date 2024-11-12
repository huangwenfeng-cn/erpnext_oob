import frappe
from pypinyin import lazy_pinyin
from erpnext_oob.monkey_patches.data import money_in_words_zh


@frappe.whitelist()
def get_pinyin(source):
    p = lazy_pinyin(source, errors='ignore')
    #全拼 和 首字母拼
    return f"{''.join(p)} {''.join(a[0] for a in p)}"

def get_posting_date_month(doc, month_key):
    """posting_date = 2023-09-18 
       d_posting_date = > 18
       m_posting_date = > 09
       y_posting_date = > 23
       Y_posting_date = > 2023
    """

    if month_key in ('d_posting_date', 'm_posting_date', 'y_posting_date', 'Y_posting_date') and hasattr(doc, "posting_date"):
        return frappe.utils.getdate(doc.posting_date).strftime(f"%{month_key[0]}")

def get_company_abbr(doc, month_key):    
    return frappe.db.get_value("Company", doc.get("company"), "abbr", cache=True)

@frappe.whitelist()
def money_in_words(number, main_currency = None, fraction_currency=None):
    return money_in_words_zh(number = number, main_currency = main_currency, fraction_currency = fraction_currency)

@frappe.whitelist()
def money_in_words_english(number):    
    from num2words import num2words

    return num2words(number)