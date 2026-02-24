import frappe


@frappe.whitelist(allow_guest=True)
def add():
	return {"name": "poovitha"}
