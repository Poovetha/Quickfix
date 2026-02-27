import frappe


def send_job_ready_email(job_card_name):
	doc = frappe.get_doc("Job Card", job_card_name)
	frappe.sendmail(recipients=[doc.customer_email], template="Job Card", args={"doc": doc})


@frappe.whitelist()
def add():
	doc = frappe.get_doc("Job Card", "JC-2026-00001", check_permission=True)
	print(doc.has_permission("write"))
	return doc.customer_name


def share_job_card(job_card_name, user_email):
	frappe.only_for("QF Manager")

	if not frappe.db.exists("Job Card", job_card_name):
		frappe.throw("Job Card is not found")

	frappe.share.add(doctype="Job Card", name=job_card_name, user=user_email, read=1, notify=1)

	return f"Job Card {job_card_name} shared with {user_email}"


def manager():
	frappe.only_for("QF Manager")

	return "Action executed successfully by Manager"
