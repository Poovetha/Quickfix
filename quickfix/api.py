import frappe


@frappe.whitelist()
def add():
	doc = frappe.get_doc("Job Card", "JC-2026-00001", check_permission=True)
	print(doc.has_permission("write"))
	return doc.customer_name
