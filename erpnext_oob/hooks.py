from . import __version__ as app_version

app_name = "erpnext_oob"
app_title = "ERPNext Out Of Box"
app_publisher = "yuzelin"
app_description = "ERPNext Out of Box"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "yuxinyong@163.com"
app_license = "MIT"


app_include_js = ["erpnext_oob.bundle.js"]
page_js = {
	"permission-manager": "public/js/hooks/page/permission_manager.js",
    "dashboard-view": "public/js/hooks/page/dashboard.js",
    "print": "public/js/hooks/page/print.js"
}
doctype_js = {
    "Company":"public/js/company.js"
}

doctype_list_js = {
    "Stock Entry":"public/js/stock_entry.js"
}

setup_wizard_requires = "assets/erpnext_oob/js/setup_wizard.js"

standard_queries = {
	"DocType": "erpnext_oob.localize.queries.doctype_role_report_query",
	"Role": "erpnext_oob.localize.queries.doctype_role_report_query",
	"Report": "erpnext_oob.localize.queries.doctype_role_report_query"
}
override_whitelisted_methods = {
    "frappe.desk.form.utils.update_comment": "erpnext_oob.overrides.update_comment",
 	"erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts.get_charts_for_country": "erpnext_oob.localize.localize.get_charts_for_country",
    #"erpnext.stock.get_item_details.get_item_details":"erpnext_oob.utils.new_get_item_details",
    "erpnext.accounts.doctype.pricing_rule.pricing_rule.apply_pricing_rule":"erpnext_oob.utils.new_apply_pricing_rule"
}

after_install = "erpnext_oob.install.after_install"

override_doctype_class = {
	"Communication": "erpnext_oob.overrides.CustomCommunication",
    "Data Import": "erpnext_oob.overrides.CustomDataImport"
}

permission_query_conditions = {
	"Customer": "erpnext_oob.permission_query.get_permission_query_conditions_customer",
    "Sales Order": "erpnext_oob.permission_query.get_permission_query_conditions_sales_order",
    "Delivery Note": "erpnext_oob.permission_query.get_permission_query_conditions_delivery_note",
    "Sales Invoice": "erpnext_oob.permission_query.get_permission_query_conditions_sales_invoice",
    "Quotation": "erpnext_oob.permission_query.get_permission_query_conditions_quotation",
    "Opportunity": "erpnext_oob.permission_query.get_permission_query_conditions_opportunity",
}
doc_events = {
 	"Customer": {
 		"validate": "erpnext_oob.doc_events.pinyin_name"
	},
    "Contact": {
 		"before_validate": "erpnext_oob.doc_events.contact_image_handling",
        "before_save": "erpnext_oob.doc_events.contact_image_handling"
	},
    "Company": {
 		"after_insert": "erpnext_oob.doc_events.company_create_default_accounts",
        "validate": "erpnext_oob.doc_events.company_create_default_accounts"
	}
}

naming_series_variables = {
    "d_posting_date": "erpnext_oob.api.get_posting_date_month",
    "m_posting_date": "erpnext_oob.api.get_posting_date_month",
    "y_posting_date": "erpnext_oob.api.get_posting_date_month",
    "Y_posting_date": "erpnext_oob.api.get_posting_date_month",
    "company_abbr": "erpnext_oob.api.get_company_abbr"
}