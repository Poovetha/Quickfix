# Copyright (c) 2026, quickfix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Technician(Document):
	def validate(self):
		frappe.rename_doc("Technician", "TECH-0003", "TECH-0004", merge=False)
		# Explain in a comment: when would merge=True be dangerous?
		#      When merge=True , it can merges two records and may delete,mix or overwrite data in the same name document which leads to data loss.
