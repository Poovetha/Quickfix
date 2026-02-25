# Copyright (c) 2026, quickfix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobCard(Document):
	def before_insert(self):
		charge = frappe.get_single_value("QuickFix Settings", "default_labour_charge")
		self.labour_charge = charge

	def validate(self):
		if not len(self.customer_phone) == 10:
			frappe.throw("Phone Number must be exactly 10 digits")
		if self.status == "In Repair" and not self.assigned__technician:
			frappe.throw("Assigned Technician is must when status is repair")

		# for parts in self.parts_used:
		# 	parts.total_price = (parts.quantity * parts.unit_price)
		# 	total += parts.total_price

		# self.parts_total = total

		# self.final_amount = self.parts_total + self.labour_charge

	def before_submit(self):
		if not self.status == "Ready for Delivery":
			frappe.throw("Not ready for delivery")

	# def on_cancel(self):
	# 	self.status == "Cancelled"
