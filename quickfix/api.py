import frappe
from frappe.utils import now


def send_job_ready_email(job_card_name):
	doc = frappe.get_doc("Job Card", job_card_name)
	frappe.sendmail(recipients=[doc.customer_email], template="Job Card", args={"doc": doc})


# audit log doctype
def log(doc, method):
	doctypes = frappe.get_all("DocType", filters={"module": "service_center"}, pluck="name")
	if doc.doctype in ["Audit log", "Error Log"]:
		return

	if doc.doctype in doctypes:
		audit = frappe.get_doc(
			{
				"doctype": "Audit log",
				"doctype_name": doc.doctype,
				"document_name": doc.name,
				"action": method,
				"user": frappe.session.user,
				"timestamp": frappe.utils.now(),
			}
		)
		audit.insert(ignore_permissions=True)


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


@frappe.whitelist()
def custom_get_count(doctype, filters=None, debug=False, cache=False):
	# First log the request to Audit Log, then call original behaviour
	frappe.get_doc(
		{
			"doctype": "Audit Log",
			"doctype_name": doctype,
			"action": "count_queried",
			"user": frappe.session.user,
			"timestamp": now(),
		}
	).insert(ignore_permissions=True)
	from frappe.client import get_count

	return get_count(doctype, filters, debug, cache)
