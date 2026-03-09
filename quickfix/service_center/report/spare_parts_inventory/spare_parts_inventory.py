# Copyright (c) 2026, quickfix and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data()

	total_parts = len(data)

	below_reorder = sum(1 for d in data if d["stock_qty"] <= d["reorder_level"])

	total_inventory_value = sum(d["total_value"] for d in data)

	report_summary = [
		{
			"value": total_parts,
			"indicator": "Blue",
			"label": _("Total Parts"),
			"datatype": "Int",
		},
		{
			"value": below_reorder,
			"indicator": "Red",
			"label": _("Below Reorder"),
			"datatype": "Int",
		},
		{
			"value": total_inventory_value,
			"indicator": "Green",
			"label": _("Total Inventory Value"),
			"datatype": "Currency",
		},
	]

	total_stock_qty = sum(d["stock_qty"] for d in data)
	total_value = sum(d["total_value"] for d in data)

	data.append(
		{
			"part_name": "TOTAL",
			"part_code": "",
			"compatible_device_type": "",
			"stock_qty": total_stock_qty,
			"reorder_level": "",
			"unit_cost": "",
			"selling_price": "",
			"margin": "",
			"total_value": total_value,
		}
	)

	return columns, data, None, None, report_summary


def get_columns():
	return [
		{"label": "Part Name", "fieldname": "part_name", "fieldtype": "Data", "width": 150},
		{"label": "Part Code", "fieldname": "part_code", "fieldtype": "Data", "width": 120},
		{"label": "Device Type", "fieldname": "device_type", "fieldtype": "Data", "width": 140},
		{"label": "Stock Qty", "fieldname": "stock_qty", "fieldtype": "Float", "width": 110},
		{"label": "Reorder Level", "fieldname": "reorder_level", "fieldtype": "Float", "width": 120},
		{"label": "Unit Cost", "fieldname": "unit_cost", "fieldtype": "Currency", "width": 120},
		{"label": "Selling Price", "fieldname": "selling_price", "fieldtype": "Currency", "width": 130},
		{"label": "Margin %", "fieldname": "margin", "fieldtype": "Percent", "width": 110},
		{"label": "Total Value", "fieldname": "total_value", "fieldtype": "Currency", "width": 130},
	]


def get_data():
	parts = frappe.db.get_all(
		"Spare Part",
		fields=[
			"part_name",
			"part_code",
			"compatible_device_type",
			"stock_qty",
			"reorder_level",
			"unit_cost",
			"selling_price",
		],
	)

	data = []

	for p in parts:
		margin = 0
		if p.selling_price:
			margin = ((p.selling_price - p.unit_cost) / p.selling_price) * 100

		total_value = p.stock_qty * p.unit_cost

		data.append(
			{
				"part_name": p.part_name,
				"part_code": p.part_code,
				"device_type": p.compatible_device_type,
				"stock_qty": p.stock_qty,
				"reorder_level": p.reorder_level,
				"unit_cost": p.unit_cost,
				"selling_price": p.selling_price,
				"margin": margin,
				"total_value": total_value,
			}
		)

	return data
