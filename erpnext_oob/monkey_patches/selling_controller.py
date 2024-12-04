import frappe
from erpnext.controllers.selling_controller import SellingController

original_validate_selling_price = SellingController.validate_selling_price
def custom_validate_selling_price(self):
    bypass_item_code, bypass_item_group = get_bypass_validate_selling_rate(self.company)
    if bypass_item_code or bypass_item_group:
        for item in self.items:
            item.is_free_item_original = item.is_free_item
            if item.item_code in bypass_item_code or item.item_group  in bypass_item_group:
                item.is_free_item = 1

    original_validate_selling_price(self)

    if bypass_item_code or bypass_item_group:
        for item in self.items:
            item.is_free_item = item.is_free_item_original

def get_bypass_validate_selling_rate(company):
    val = frappe.cache().hget('bypass_validate_selling_rate', company)

    if not val:
        data = frappe.get_all('Bypass Validate Selling Rate', filters={'company': company, 'active': 1},
                            fields=['item_code', 'item_group'])
        bypass_item_code = {d.item_code for d in data if d.item_code}
        bypass_item_group = {d.item_group for d in data if d.item_group}
        frappe.cache().hset('bypass_validate_selling_rate', company, (bypass_item_code, bypass_item_group))
        val = frappe.cache().hget('bypass_validate_selling_rate', company)

    return val
apps =frappe.get_installed_apps()
if 'erpnext_oob' in frappe.get_installed_apps():
    SellingController.validate_selling_price = custom_validate_selling_price
