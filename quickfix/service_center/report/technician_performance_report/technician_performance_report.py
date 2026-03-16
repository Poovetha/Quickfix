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
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_report_summary(data)

	return columns, data, None, chart, summary


def get_columns(filter=None):
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	columns = [
		{
			"label": "Technician",
			"fieldname": "technician",
			"fieldtype": "Link",
			"options": "Technician",
			"width": 150,
		},
		{
			"label": "Total Jobs",
			"fieldname": "total_jobs",
			"fieldtype": "Int",
			"width": 120,
		},
		{
			"label": "Completed",
			"fieldname": "completed",
			"fieldtype": "Int",
			"width": 120,
		},
		{
			"label": "Avg Turnaround Days",
			"fieldname": "avg_turnaround_days",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": "Revenue",
			"fieldname": "revenue",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "Completion Rate %",
			"fieldname": "completion_rate_percentage",
			"fieldtype": "Percent",
			"width": 150,
		},
	]

	device_types = frappe.get_all("Device Type", fields=["name"])

	for dt in device_types:
		columns.append(
			{
				"label": dt.name,
				"fieldname": dt.name.lower().replace(" ", "_"),
				"fieldtype": "Int",
				"width": 100,
			}
		)

	return columns


def get_data(filters=None):
	conditions = {}

	if filters:
		if filters.get("technician"):
			conditions["technician"] = filters.get("technician")

		if filters.get("from_date") and filters.get("to_date"):
			conditions["posting_date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]

	jobs = frappe.get_list(
		"Job Card",
		filters=conditions,
		fields=["technician", "status", "device_type", "final_amount"],
	)

	device_types = frappe.get_all("Device Type", fields=["name"])
	tech_map = {}

	for job in jobs:
		tech = job.get("technician")

		if tech not in tech_map:
			tech_map[tech] = {
				"technician": tech,
				"total_jobs": 0,
				"completed": 0,
				"revenue": 0,
				"avg_turnaround_days": 0,
			}

			for dt in device_types:
				field = dt.name.lower().replace(" ", "_")
				tech_map[tech][field] = 0

		tech_map[tech]["total_jobs"] += 1

		if job.get("status") == "Completed":
			tech_map[tech]["completed"] += 1

		tech_map[tech]["revenue"] += job.get("final_amount") or 0

		if job.get("device_type"):
			field = job.get("device_type").lower().replace(" ", "_")

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


def get_chart(data):
	labels = []
	total = []
	completed = []

	for d in data:
		labels.append(d.get("technician"))
		total.append(d.get("total_jobs"))
		completed.append(d.get("completed"))

	chart = {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": "Total Jobs", "values": total},
				{"name": "Completed", "values": completed},
			],
		},
		"type": "bar",
	}

	return chart


def get_report_summary(data):
	total_jobs = 0
	total_revenue = 0
	best_technician = ""

	max_completed = 0

	for d in data:
		total_jobs += d.get("total_jobs", 0)
		total_revenue += d.get("revenue", 0)

		if d.get("completed", 0) > max_completed:
			max_completed = d.get("completed")
			best_technician = d.get("technician")

	summary = [
		{"label": "Total Jobs", "value": total_jobs, "indicator": "Blue"},
		{"label": "Total Revenue", "value": total_revenue, "indicator": "Green"},
		{"label": "Best Technician", "value": best_technician, "indicator": "Orange"},
	]

	return summary
