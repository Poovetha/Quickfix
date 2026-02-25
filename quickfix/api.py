import frappe


def send_job_ready_email(job_card_name):
	doc = frappe.get_doc("Job Card", job_card_name)
	frappe.sendmail(recipients=[doc.customer_email], template="Job Card", args={"doc": doc})


@frappe.whitelist()
def add():
	doc = frappe.get_doc("Job Card", "JC-2026-00001", check_permission=True)
	print(doc.has_permission("write"))
	return doc.customer_name
