import frappe, csv, os, json
from frappe import _
from erpnext.accounts.doctype.chart_of_accounts_importer.chart_of_accounts_importer import (
	unset_existing_data,build_forest
)
from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import create_charts,build_tree_from_json
from erpnext.setup.setup_wizard.operations.taxes_setup import from_detailed_data
from erpnext.accounts.utils import get_coa as old_get_coa
from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import (
	get_charts_for_country as old_get_charts_for_country,
	get_chart as original_get_chart,
	build_tree_from_json
)

def import_coa(company, chart_template = None):
	unset_existing_data(company)
	if not chart_template or chart_template == '中国会计科目表':
		data = get_chart_data_from_csv()
		frappe.local.flags.ignore_root_company_validation = True
		forest = build_forest(data)
		from_coa_importer = True			
	else:
		forest = get_chart(chart_template)
		from_coa_importer = False		
	create_charts(company, custom_chart=forest, from_coa_importer=from_coa_importer)
	set_default_accounts(company)
	set_global_defaults()
	set_system_settings()
	change_field_property()
	setup_tax_template(company)
	setup_tax_rule(company)
	set_item_group_account(company)
	set_warehouse_account(company)

def get_chart(chart_template, existing_company=None):
    if not chart_template in ['中国小企业会计准则', '中国企业会计准则']:
        return original_get_chart(chart_template, existing_company)
    else:		
        path = frappe.get_app_path('erpnext_oob','localize/chart_of_account')
        fname = frappe.as_unicode(chart_template)    
        with open(os.path.join(path, f'{fname}.json'), "r") as f:
            chart = f.read()
            if chart and json.loads(chart).get("name") == chart_template:
                return json.loads(chart).get("tree")

def get_chart_data_from_csv(as_dict=False):
	file_path = os.path.join(os.path.dirname(__file__), 'coa_cn.csv')
	data = []
	with open(file_path, 'r') as in_file:
		csv_reader = list(csv.reader(in_file))
		headers = csv_reader[0]
		del csv_reader[0] # delete top row and headers row

		for row in csv_reader:
			if as_dict:
				data.append({frappe.scrub(header): row[index] for index, header in enumerate(headers)})
			else:
				if not row[1]:
					row[1] = row[0]
					row[3] = row[2]
				data.append(row)							
	return data

def set_default_accounts(company):
	file_path = os.path.join(os.path.dirname(__file__), 'default_accounts.csv')
	with open(file_path, 'r') as in_file:
		data = list(csv.reader(in_file))

	company = frappe.get_doc('Company', company)
	company_name = company.name		
	values = {d[0]:frappe.db.get_value("Account",{"company": company_name, "account_name": d[1], "is_group": 0})
				for d in data}
	company.update(values)
	company.save()
	return values

def set_global_defaults():
	frappe.db.set_single_value('Global Defaults',
		{
			'disable_rounded_total':1,
			'disable_in_words':1
		}
	)

def set_system_settings():
	frappe.db.set_single_value('System Settings',
		{
			'rounding_method': 'Commercial Rounding',
			'allow_login_using_user_name': 1,
			'allow_login_using_mobile_number': 1,
			'currency_precision': 2,
			'float_precision': 4,
			'date_format': 'yyyy-mm-dd'
		}
	)

def change_field_property():
	if bool(frappe.db.get_single_value('System Settings', 'setup_complete')):
		return
	file_path = os.path.join(os.path.dirname(__file__), 'field_property.csv')
	with open(file_path, 'r') as in_file:
		data = list(csv.reader(in_file))
	try:
		for (doctype, field_name, prop, value) in data:
			frappe.get_doc({
				'doctype': 'Property Setter',
				'doctype_or_field': 'DocField',
				'doc_type': doctype,
				'field_name': field_name,
				'property': prop,
				'value': value
			}).insert(ignore_permissions=1)
	except:
		pass

def setup_tax_template(company_name):
	file_path = os.path.join(os.path.dirname(__file__), 'tax_template.json')
	with open(file_path, 'r') as json_file:
		tax_data = json.load(json_file)
	from_detailed_data(company_name, tax_data)

	try:
		#标准功能中未处理含税字段，这里单独处理
		for prefix in ('Purchase', 'Sales'):	
			header = frappe.qb.DocType(f"{prefix} Taxes and Charges Template")
			detail = frappe.qb.DocType(f"{prefix} Taxes and Charges")

			frappe.qb.update(detail
				).join(header
				).on(header.name == detail.parent
				).where(header.title.like('%含税%')
				).set(detail.included_in_print_rate, 1
				).run()			
	except:
		pass

def setup_tax_rule(company_name):
	try:
		abbr = frappe.db.get_value('Company', company_name, 'abbr')
		file_path = os.path.join(os.path.dirname(__file__), 'tax_rule.csv')
		with open(file_path, 'r') as in_file:
			data = list(csv.reader(in_file))
		if data: data = data[1:]
		for (tax_category, tax_type, customer_group, item_group, billing_country,
			shipping_country, priority, tax_template) in data:
			template_field_name = 'purchase_tax_template' if tax_type =='Purchase' else 'sales_tax_template'
			tax_rule = frappe.get_doc({
					'doctype':'Tax Rule',
					'tax_category': tax_category,
					'tax_type': tax_type,
					'customer_group': customer_group,
					'item_group': item_group,
					'billing_country': billing_country,
					'shipping_country': shipping_country,
					'priority': priority,
					template_field_name: f'{tax_template} - {abbr}',
					'company': company_name})
			tax_rule.insert(ignore_permissions = 1)	
	except:
		pass

@frappe.whitelist()
def get_charts_for_country(country, with_standard=False):
	charts = old_get_charts_for_country(country, with_standard)
	if country == 'China':
		charts.insert(0,'中国小企业会计准则')
		charts.extend(['中国企业会计准则'])
	return charts	

def set_warehouse_account(company):
	abbr = frappe.db.get_value('Company', company, 'abbr')
	for wh_detail in [
		[_("Finished Goods"), '1405 - 库存商品' ],
		[_("Goods In Transit"), '1411 - 周转材料']]:
		warehouse_name = f'{wh_detail[0]} - {abbr}'		
		account_name = 	f'{wh_detail[1]} - {abbr}'	
		frappe.db.set_value('Warehouse', warehouse_name, 'account', account_name)

def set_item_group_account(company):
	try:
		item_group_account_list =  [
					[_("Raw Material"), '生产成本-基本生产成本'],
					[_("Sub Assemblies"), '生产成本-基本生产成本'],
					[_("Consumable"), '生产成本-基本生产成本'],
					[_("Services"), '生产成本-辅助生产成本'],
					[_("Product"), '主营业务成本']
		]
		
		account_map = frappe._dict(frappe.get_all('Account',
			filters ={'account_name': ('in', [row[1] for row in item_group_account_list]),
			         'company': company},
			fields = ['account_name', 'name'],
			as_list = True))
		for (item_group, account_name) in item_group_account_list:
			account_id = account_map.get(account_name)
			if account_id and frappe.db.exists('Item Group', item_group):				
				item_group_doc = frappe.get_doc('Item Group', item_group)				
				item_group_doc.append('item_group_defaults',{
					'company': company,
					'expense_account': account_id
				})
				item_group_doc.save()
	except:
		pass	