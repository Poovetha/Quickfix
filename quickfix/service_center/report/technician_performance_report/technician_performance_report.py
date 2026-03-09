# Copyright (c) 2026, quickfix and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data()
	chart = get_chart(data)
	summary = get_report_summary(data)

	return columns, data, None, chart, summary


def get_columns(filter=None):
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	column = [
		{
			"label": "Technician",
			"fieldname": "technician",
			"fieldtype": "Link",
			"options": "Technician",
			"width": 120,
		},
		{"label": "Total Jobs", "fieldname": "total_jobs", "fieldtype": "Int", "width": 120},
		{"label": "Completed", "fieldname": "completed", "fieldtype": "Int", "width": 120},
		{
			"label": "Avg Turnaround Days",
			"fieldname": "avg_turnaround_days",
			"fieldtype": "Float",
			"width": 120,
		},
		{"label": "Revenue", "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
		{
			"label": "Completion Rate %",
			"fieldname": "completion_rate_percentage",
			"fieldtype": "Percent",
			"width": 120,
		},
	]

	device_types = frappe.get_all("Device Type", fields=["name"])

	for dt in device_types:
		column.append(
			{
				"label": dt.name,
				"fieldname": dt.name.lower().replace(" ", "_"),
				"fieldtype": "Int",
				"width": 100,
			}
		)

	return column


def get_chart(data):
	labels = []
	total_jobs = []
	completed_jobs = []

	for d in data:
		labels.append(d.get("technician"))
		total_jobs.append(d.get("total_jobs"))
		completed_jobs.append(d.get("completed"))

	chart = {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": "Total Jobs", "values": total_jobs},
				{"name": "Completed", "values": completed_jobs},
			],
		},
		"type": "bar",
	}

	return chart


def get_report_summary(data):
	total_jobs = sum(d.get("total_jobs", 0) for d in data)
	total_revenue = sum(d.get("revenue", 0) for d in data)
	best_technician = max(data, key=lambda x: x.get("completed", 0)) if data else {}
	summary = [
		{"label": "Total Jobs", "value": total_jobs, "indicator": "Red"},
		{"label": "Total Revenue", "value": total_revenue, "indicator": "Green"},
		{"label": "Best Technician", "value": best_technician.get("technician"), "indicator": "Blue"},
	]
	return summary


def get_data(filters=None):
	jobs = frappe.get_list("Job Card", fields=["technician", "status", "device_type", "final_amount"])

	tech_map = {}
	device_types = frappe.get_all("Device Type", fields=["name"])
	for job in jobs:
		tech = job.technician
		if tech not in tech_map:
			tech_map[tech] = {"technician": tech, "total_jobs": 0, "completed": 0, "revenue": 0}

			for dt in device_types:
				field = dt.name.lower().replace(" ", "_")
				tech_map[tech][field] = 0

		tech_map[tech]["total_jobs"] += 1

		if job.status == "Completed":
			tech_map[tech]["completed"] += 1

		tech_map[tech]["revenue"] += job.final_amount or 0

		if job.device_type:
			field = job.device_type.lower().replace(" ", "_")
			if field in tech_map[tech]:
				tech_map[tech][field] += 1

	data = []

	for tech in tech_map.values():
		if tech["total_jobs"] > 0:
			tech["completion_rate_percentage"] = (tech["completed"] / tech["total_jobs"]) * 100
		else:
			tech["completion_rate_percentage"] = 0
		tech["avg_turnaround_days"] = 2
		data.append(tech)

	return data


def prepare_report(filters=None):
	frappe.enqueue(
		method="frappe.desk.query_report.run",
		queue="long",
		timeout=600,
		report_name="Technician Performance Report",
		filters=filters,
		user=frappe.session.user,
	)
