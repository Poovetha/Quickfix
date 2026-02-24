import frappe


@frappe.whitelist(allow_guest=True)
def add():
	# a = 10
	# b = 0
	# c = a / b
	return {"name": "poovitha"}
