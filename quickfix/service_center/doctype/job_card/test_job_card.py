# Copyright (c) 2026, quickfix and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestJobCard(IntegrationTestCase):
	pass


def make_device_type():
	if not frappe.db.exists("Device Type", "Mobile"):
		doc = frappe.get_doc({"doctype": "Device Type", "device_type_name": "Mobile"})
		doc.insert(ignore_permissions=True)
		return doc

	return frappe.get_doc("Device Type", "Mobile")


def make_technician():
	if not frappe.db.exists("Technician", "Test Technician"):
		doc = frappe.get_doc(
			{"doctype": "Technician", "technician_name": "Test Technician", "status": "Active"}
		)
		doc.insert(ignore_permissions=True)
		return doc

	return frappe.get_doc("Technician", "Test Technician")


def make_spare_part(stock_qty=10):
	if not frappe.db.exists("Spare Part", "PART-001"):
		doc = frappe.get_doc(
			{
				"doctype": "Spare Part",
				"part_code": "PART-001",
				"part_name": "Test Part",
				"stock_qty": stock_qty,
			}
		)
		doc.insert(ignore_permissions=True)
		return doc

	part = frappe.get_doc("Spare Part", "PART-001")
	part.stock_qty = stock_qty
	part.save(ignore_permissions=True)
	return part


def make_job_card(**kwargs):
	device = make_device_type()
	technician = make_technician()

	data = {
		"doctype": "Job Card",
		"customer_name": "Test Customer",
		"customer_email": "test@example.com",
		"device_type": device.name,
		"device_model": "Samsung",
		"technician": technician.name,
		"complaint": "Battery issue",
		"status": "Open",
	}

	data.update(kwargs)

	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)

	return doc
