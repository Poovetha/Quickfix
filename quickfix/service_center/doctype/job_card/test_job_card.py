# Copyright (c) 2026, quickfix and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import random_string

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestJobCard(IntegrationTestCase):
	def setUp(self):
		create_device_type()
		create_technician()
		create_spare_part()

	def test_happy_path_insert(self):
		job = create_job_card()
		exists = frappe.db.exists("Job Card", job.name)

		self.assertTrue(exists)
		self.assertEqual(job.docstatus, 0)

	def test_phone_validation(self):
		self.assertRaises(frappe.ValidationError, create_job_card, customer_phone="12345")
		self.assertRaises(frappe.ValidationError, create_job_card, customer_phone="123456789012")

		self.assertRaises(frappe.ValidationError, create_job_card, customer_phone="98765abcde")

		job = create_job_card(customer_phone="9876543210")

		self.assertTrue(job.name)

	def test_spare_part_price_validation(self):
		self.assertRaises(frappe.ValidationError, create_spare_part, unit_cost=100, selling_price=100)

		self.assertRaises(frappe.ValidationError, create_spare_part, unit_cost=100, selling_price=90)

		part = create_spare_part(unit_cost=100, selling_price=101)

		self.assertTrue(part.name)


def create_device_type():
	if not frappe.db.exists("Device Type", "Laptop"):
		device = frappe.get_doc({"doctype": "Device Type", "device_type": "Laptop"})
		device.insert()
		return device
	else:
		return frappe.get_doc("Device Type", "Laptop")


def create_technician():
	if not frappe.db.exists("Technician", "Test Technician"):
		technician = frappe.get_doc(
			{
				"doctype": "Technician",
				"technician_name": "Test Technician",
			}
		)
		technician.insert()
		return technician
	else:
		return frappe.get_doc("Technician", "Test Technician")


def create_spare_part(stock_qty=10, unit_cost=100, selling_price=150):
	part = frappe.get_doc(
		{
			"doctype": "Spare Part",
			"part_code": "TEST-" + random_string(5),
			"part_name": "Test Part",
			"stock_qty": stock_qty,
			"unit_cost": unit_cost,
			"selling_price": selling_price,
		}
	)

	part.insert()
	return part


def create_job_card(**kwargs):
	data = {
		"doctype": "Job Card",
		"customer_name": "Test Customer",
		"customer_phone": "9876543210",
		"customer_email": "poovethapalanivelu@gmail.com",
		"device_type": "Laptop",
		"problem_description": "Screen problem",
	}

	data.update(kwargs)

	job = frappe.get_doc(data)
	job.insert()

	return job
