# Copyright (c) 2026, quickfix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class SparePart(Document):
	def autoname(self):
		if not self.part_code:
			frappe.throw("Part code must be entered")
		else:
			self.name = self.part_code.upper() + "-" + make_autoname("PART-.YYYY.-.####")

	def validate(self):
		if self.selling_price < self.unit_cost:
			frappe.throw("Selling Price must be high")
