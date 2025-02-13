import frappe
from frappe.core.doctype.user_permission.user_permission import get_user_permissions
from erpnext_oob.api import get_cached_value


def get_permission_query_conditions_customer(user: str | None = None) -> str:
    return get_sales_person_sub_query(user=user, fieldname="name")

def get_permission_query_conditions_sales_order(user: str | None = None) -> str:
    return get_sales_person_sub_query(user=user)

def get_permission_query_conditions_delivery_note(user: str | None = None) -> str:
    return get_sales_person_sub_query(user=user)

def get_permission_query_conditions_sales_invoice(user: str | None = None) -> str:
    return get_sales_person_sub_query(user=user)

def get_permission_query_conditions_quotation(user: str | None = None) -> str:
    conditions = get_sales_person_sub_query(user=user, fieldname="party_name")
    if conditions:
        conditions = f"( quotation_to <> 'Customer' or {conditions})"
    return conditions

def get_permission_query_conditions_opportunity(user: str | None = None) -> str:
    conditions = get_sales_person_sub_query(user=user, fieldname="party_name")
    if conditions:
        conditions = f"( opportunity_from <> 'Customer' or {conditions} )"
    return conditions

def get_sales_person_sub_query(user=None, fieldname="customer"):
    """
    获取以当前用户被授权的业务员为条件的子查询
    """

    user = user or frappe.session.user
    if not get_cached_value("enable_sales_person_permission") or user == "Administrator":
        return ""

    user_doc = frappe.get_doc('User', user)
    has_special_role = [r for r in user_doc.roles if r.role == 'System Manager']
    conditions = ''                                                                  #默认返回空
    if not has_special_role:        
        user_permissions = get_user_permissions(user = frappe.user)                            #获取定义的用户权限记录
        sales_person_list = [u.doc for u in user_permissions.get('Sales Person') or []]     #摘取业务员被授权业务员清单
        if sales_person_list:                                                               #仅在用户权限中分派了业务员时，添加过滤条件
            # 用户权限限制里勾选了默认，表示用户是业务员
            owner_list = frappe.get_all("User Permission", distinct=1, pluck="user",
                filters={'for_value':("in",sales_person_list), 'is_default':1, 'allow':"Sales Person"}) or [""]
            customer = frappe.qb.DocType('Customer').as_('my_customer')     
            sales_team = frappe.qb.DocType('Sales Team').as_('my_sales_team')
            sub_query_sql = frappe.qb.from_(customer
                ).left_join(sales_team
                ).on(customer.name ==  sales_team.parent
                ).select(customer.name
                ).where((customer.owner.isin(owner_list)) | (sales_team.sales_person.isin(sales_person_list))
                )
            conditions = f'{fieldname} in ({sub_query_sql})'                          #返回where条件语句:子查询语句
    return conditions