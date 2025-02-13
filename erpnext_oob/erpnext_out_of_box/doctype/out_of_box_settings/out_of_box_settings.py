# Copyright (c) 2025, yuzelin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

custom_fields = {
	"enable_sales_person_permission":[],	
}

class OutOfBoxSettings(Document):
	def on_update(self):
		before_save = self.get_doc_before_save()
		for key in custom_fields.keys():
			if (not before_save or before_save.get(key) != self.get(key)):
				frappe.cache().delete_value(key)
				if self.get(key):
					self.create_custom_fields(key)
				else:
					self.remove_custom_fields(key)		

	def create_custom_fields(self, key):
		fields = custom_fields.get(key) or []
		for df in fields:
			if not frappe.db.exists('Custom Field', df.get('name')):
				create_custom_field(df.get('dt'), df, ignore_validate=True)

	def remove_custom_fields(self, key):
		fields = custom_fields.get(key) or []
		for df in fields:
			if frappe.db.exists('Custom Field', df.get('name')):
				frappe.delete_doc("Custom Field", df.get('name'))