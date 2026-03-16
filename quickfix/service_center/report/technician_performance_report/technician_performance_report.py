# Copyright (c) 2026, quickfix and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_report_summary(data)

	return columns, data, None, chart, summary


def get_columns():
	columns = [
		{
			"label": "Technician",
			"fieldname": "technician",
			"fieldtype": "Data",
			"width": 180,
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
				"width": 110,
			}
		)

	return columns


def get_data(filters=None):
	conditions = {}

	if filters:
		if filters.get("technician"):
			conditions["assigned__technician"] = filters.get("technician")

		if filters.get("from_date") and filters.get("to_date"):
			conditions["creation"] = [
				"between",
				[filters.get("from_date"), filters.get("to_date")],
			]

	jobs = frappe.get_list(
		"Job Card",
		filters=conditions,
		fields=["assigned__technician", "status", "device_type", "final_amount"],
	)

	device_types = frappe.get_all("Device Type", fields=["name"])

	tech_map = {}

	for job in jobs:
		tech_id = job.get("assigned__technician")

		if tech_id:
			tech = frappe.db.get_value("Technician", tech_id, "technician_name")
		else:
			tech = "Unassigned"

		if tech not in tech_map:
			tech_map[tech] = {
				"technician": tech,
				"total_jobs": 0,
				"completed": 0,
				"revenue": 0,
				"avg_turnaround_days": 2,
			}

			for dt in device_types:
				field = dt.name.lower().replace(" ", "_")
				tech_map[tech][field] = 0

		tech_map[tech]["total_jobs"] += 1

		if job.get("status") == "Delivered":
			tech_map[tech]["completed"] += 1

		frappe.log_error(tech_map[tech]["completed"])

		tech_map[tech]["revenue"] += job.get("final_amount") or 0

		device = job.get("device_type")

		if device:
			field = device.lower().replace(" ", "_")

			if field in tech_map[tech]:
				tech_map[tech][field] += 1

	data = []

	for tech in tech_map.values():
		if tech["total_jobs"] > 0:
			tech["completion_rate_percentage"] = (tech["completed"] / tech["total_jobs"]) * 100
		else:
			tech["completion_rate_percentage"] = 0

		data.append(tech)

	return data


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
				{"name": "Completed Jobs", "values": completed_jobs},
			],
		},
		"type": "bar",
		"colors": ["Pink", "Blue"],
		"barOptions": {"stacked": False},
	}

	return chart


def get_report_summary(data):
	total_jobs = 0
	total_revenue = 0
	best_technician = "None"

	max_completed = -1

	for d in data:
		total_jobs += d.get("total_jobs", 0)
		total_revenue += d.get("revenue", 0)

		if d.get("completed", 0) > max_completed:
			max_completed = d.get("completed")
			best_technician = d.get("technician")

	summary = [
		{"label": "Total Jobs", "value": total_jobs, "indicator": "Blue"},
		{"label": "Total Revenue", "value": total_revenue, "indicator": "Green"},
		{"label": "Best Technician", "value": best_technician, "indicator": "Violet"},
	]

	return summary
