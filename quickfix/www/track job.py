import frappe


def get_context(context):
	context.title = "Track Job"
	context.description = "Track the status of your job"
	context.og_title = "Track Job Status"

	job_card = frappe.form_dict.get("job_card")

	if job_card:
		context.job = frappe.db.get_value(
			"Job Card", job_card, ["name", "status", "customer_name"], as_dict=True
		)
