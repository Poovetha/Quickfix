import re
from datetime import date

import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import now, today


def send_job_ready_email(name):
	doc = frappe.get_doc("Job Card", name)
	pdf = frappe.get_print("Job Card", doc.name, print_format="Job Card", as_pdf=True)
	try:
		frappe.sendmail(
			recipients=[doc.customer_email],
			template="Job Card",
			args={"doc": doc},
			attachments=[{"fname": f"{doc.name}.pdf", "fcontent": pdf}],
		)
	except Exception:
		frappe.log_error(title="Email Sending Failed", message=frappe.get_traceback())


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


def check_low_stock():
	last_run = frappe.db.get_value("Audit Log", {"action": "low_stock_check", "date": today()}, "name")

	if last_run:
		return

	else:
		frappe.get_doc({"doctype": "Audit Log", "action": "low_stock_check", "date": today()}).insert(
			ignore_permissions=True
		)


# def test_error_job():
# 	a = 10 / 0


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


def monthly_revenue_report():
	delivered_jobs = frappe.get_all("Job Card", filters={"status": "Delivered"}, fields=["total_amount"])
	total_revenue = 0
	for job in delivered_jobs:
		total_revenue += job.total_amount or 0
	frappe.logger.info(f"Total Monthly Revenue: {total_revenue}")


def cancel_draft_job_cards():
	frappe.db.sql("""
        UPDATE `tabJob Card`
        SET status = 'Cancelled'
        WHERE status = 'Draft'
        LIMIT 1000
    """)
	frappe.db.commit()


def bulk_insert():
	values = [(f"LOG-{i}", "Bulk_insert", now()) for i in range(500)]

	frappe.db.bulk_insert("Audit Log", ["name", "action", "timestamp"], values)


def test_secret():
	test = frappe.conf.get("payment_api_key")
	print(test)
	return test


@frappe.whitelist()
def failure():
	raise Exception("Background job failure")


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


def get_status_chart_data():
	cache_key = "quickfix_status_chart"
	cached_data = frappe.cache.get_value(cache_key)
	if cached_data:
		return cached_data

	data = frappe.db.sql(
		"""
		SELECT status, COUNT(name) as count
		FROM `tabJob Card`
		GROUP BY status
	""",
		as_dict=True,
	)

	labels = []
	values = []

	for d in data:
		labels.append(d.status)
		values.append(d.count)

	frappe.cache.set_value(cache_key, data, expires_in_sec=300)

	return {"labels": labels, "datasets": [{"name": "Job Cards", "values": values}]}


@frappe.whitelist(allow_guest=True)
def get_job_summary():
	job_card_name = frappe.form_dict.get("job_card_name")

	if not job_card_name:
		frappe.local.response["http_status_code"] = 404
		return {"error": "Not found"}

	job_card = frappe.db.get_value(
		"Job Card", job_card_name, ["name", "customer_name", "status", "creation"], as_dict=True
	)

	if not job_card:
		frappe.local.response["http_status_code"] = 404
		return {"error": "Not found"}

	return {
		"job_card_name": job_card.name,
		"customer_name": job_card.customer_name,
		"status": job_card.status,
		"created_on": job_card.creation,
		"summary_generated_on": date.today(),
	}


@frappe.whitelist(allow_guest=True)
def get_job_by_phone():
	ip = frappe.local.request_ip
	key = f"rate_limit:{ip}"

	count = frappe.cache().get(key) or 0
	if int(count) >= 5:
		frappe.local.response["http_status_code"] = 429
		return {"error": "Too many requests"}

	frappe.cache().set(key, int(count) + 1, 60)
	return {"success": "Request allowed"}


@frappe.whitelist()
def trigger_error():
	frappe.enqueue("quickfix.api.test_error_job", queue="default")


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=10, seconds=60)
def track_job(phone):
	phone = re.sub(r"\D", "", phone)[:10]

	if not phone:
		frappe.throw("Invalid phone number")

	jobs = frappe.get_all("Job Card", filters={"customer_phone": phone}, fields=["name", "status"])

	if not jobs:
		frappe.throw("No jobs found for this phone")

	return jobs
