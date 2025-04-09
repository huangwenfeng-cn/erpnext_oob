import frappe
from erpnext_oob.api import get_pinyin, get_cached_value
from erpnext_oob.localize.localize import import_coa


def pinyin_name(doc, method):
    if not doc.meta.has_field('pinyin_name'): return
    pinyin_name = get_pinyin(doc.customer_name)
    if pinyin_name.strip():    
        doc.pinyin_name = pinyin_name

def contact_image_handling(doc, method):
    if method == "before_validate" and not doc.image:
        doc.image = "dummy_image"
    elif method == "before_save" and doc.image == "dummy_image":
        doc.image = None

def company_create_default_accounts(doc, method):
    coa_exist = frappe.db.sql(
			"""select name from tabAccount
				where company=%s and docstatus<2 limit 1""",
			doc.name
		)
    if not coa_exist and doc.chart_of_accounts in  ['中国会计科目表','中国小企业会计准则', '中国企业会计准则'] and not doc.is_new():
        doc.create_default_warehouses()
        frappe.local.flags.ignore_root_company_validation = True
        frappe.local.flags.ignore_chart_of_accounts = True      #bypass system to set default accounts
        import_coa(doc.name, doc.chart_of_accounts)        

def sync_employee_user_permission(doc, method):
    """
    删除或添加维护的员工对应的用户权限限制记录
    """    

    def record_count():
        return frappe.db.count("User Permission", {
                    "user": user,
                    "allow": doc.doctype,
                    "for_value": doc.name
                })

    if doc.has_value_changed("employee") and get_cached_value("enable_sales_person_permission"):
        before_save = doc.get_doc_before_save()
        old_employee = before_save.employee if before_save else None
        new_employee = doc.employee
        employee_user_map = frappe._dict(frappe.get_all("Employee", 
            filters = {
                "name": ("in", [old_employee, new_employee])
            },
            fields=["name", "user_id"],
            as_list=1
        ))
        if new_employee:
            user = employee_user_map.get(new_employee)
            if user and not record_count():
                user_permission_doc = frappe.new_doc("User Permission")
                user_permission_doc.update({
                    "user": user,
                    "allow": doc.doctype,
                    "for_value": doc.name
                }).insert(
                    ignore_permissions=True, 
                    ignore_if_duplicate=True,
                    ignore_links=True
                )
        if old_employee:
            user = employee_user_map.get(old_employee)
            if user:
                cnt = record_count()
                # 只有一笔记录，修改为不存在的值，以免可查看所有客户
                if cnt == 1:
                    frappe.db.set_value("User Permission", {
                        "user": user,
                        "allow": doc.doctype,
                        "for_value": doc.name
                    }, "for_value", "dummy_sales_person")
                elif cnt > 1:
                    frappe.db.delete("User Permission", {
                        "user": user,
                        "allow": doc.doctype,
                        "for_value": doc.name
                    })