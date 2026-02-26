# Copyright (c) 2026, quickfix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class JobCard(Document):
	def validate(self):
		self.labour_charge = frappe.get_single_value("QuickFix Settings", "default_labour_charge")
		if not len(self.customer_phone) == 10:
			frappe.throw("Phone Number must be exactly 10 digits")
		if self.status == "In Repair" and not self.assigned__technician:
			frappe.throw("Assigned Technician is must when status is repair")
		total = 0
		for parts in self.parts_used:
			parts.total_price = parts.quantity * parts.unit_price
			total += parts.total_price

		self.parts_total = total

		self.final_amount = self.parts_total + self.labour_charge

		if not self.customer_email:
			frappe.throw("Email is required ")

	def before_submit(self):
		if not self.status == "Ready for Delivery":
			frappe.throw("Not ready for delivery")

		for parts in self.parts_used:
			stock = frappe.get_value("Spare Part", {"part_name": parts.part_name}, ["stock_qty"]) or 0
			if stock < parts.quantity:
				frappe.throw(f"{parts.part_name}is out of stock")

	def on_submit(self):
		for parts in self.parts_used:
			stock = frappe.get_value("Spare Part", {"part_name": parts.part_name}, ["stock_qty"]) or 0
			final = stock - parts.quantity
			frappe.db.set_value(
				"Spare Part", {"part_name": parts.part_name}, "stock_qty", final, ignore_permissions=True
			)
			# Here ignore_permissions is for if anyone dont have permission to modify the spare part doctype ,
			# this will bypass the permission and set the value. It is needed because it is systematic logic.

		invoice = frappe.get_doc(
			{
				"doctype": "Service Invoice",
				"job_card": self.name,
				"customer_name": self.customer_name,
				"invoice_date": now(),
				"labour_charge": self.labour_charge,
				"parts_total": self.parts_total,
				"total_amount": self.final_amount,
				"payment_status": "Unpaid",
			}
		)
		invoice.insert(ignore_permissions=True)

		# frappe.publish_realtime() sends real-time updates from the server to the user interface without page refresh via socket io.frappe.publish_realtime() is used to send live updates from the server to the browser instantly.No page refresh needed
		frappe.publish_realtime("job_ready", {"job_card": self.name}, user=self.owner)

		frappe.enqueue(method="quickfix.api.send_job_ready_email", job_card_name=self.name)

	def on_cancel(self):
		self.status = "Cancelled"
		for parts in self.parts_used:
			stock = frappe.get_value("Spare Part", {"part_name": parts.part_name}, ["stock_qty"]) or 0
			final = stock + parts.quantity
			frappe.db.set_value(
				"Spare Part", {"part_name": parts.part_name}, "stock_qty", final, ignore_permissions=True
			)

		doc = frappe.db.get_value("Service Invoice", {"job_card": self.name, "docstatus": 1}, "name")
		if doc:
			invoice = frappe.get_doc("Service Invoice", doc)
			invoice.cancel()

	def on_trash(self):
		if not self.status == "Cancelled" and not self.status == "Draft":
			frappe.throw("Cant cancel the job card, Only draft or cancelled can be deleted ")
