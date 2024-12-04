import frappe
from frappe.defaults import get_defaults
from frappe import defaults


def custom_get_defaults(user=None):
    """
    多公司场景下，默认公司设置在用户默认值而非全局默认值中
    """
    defaults = get_defaults(user = user)
    if user:
        defaults.update(frappe._dict(
            frappe.get_all(
                'User Default', 
                filters={'user': user}, 
                fields=['setting_key','setting_value'],
                as_list = 1
            )
        ))
    return defaults

apps =frappe.get_installed_apps()
if 'erpnext_oob' in frappe.get_installed_apps():
    defaults.get_defaults = custom_get_defaults