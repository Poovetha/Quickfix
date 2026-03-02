import frappe
from frappe import ValidationError
from frappe.tests.utils import FrappeTestCase


def after_install():
	device = ["Laptop", "Tablet", "Smartphone"]
	for dev in device:
		if not frappe.db.exists("Device Type", dev):
			doc = frappe.get_doc({"Doctype": "Device Type", "device_type": dev})
			doc.insert()

		if not frappe.db.exists("Quickfix Settings"):
			doc = frappe.get_doc(
				{
					"Doctype": "Quickfix Settings",
					"shop_name": "Quickfix services",
					"manager_email": "poovethapalanivelu1@gmail.com",
					"default_labour_charge": 400,
					"low_stock_alert_enabled": 1,
				}
			)
			doc.insert()
		else:
			return "done"


def before_uninstall():
	sub = frappe.db.count("Job Card", {"docstatus": "1"})
	if sub > 0:
		raise ValidationError(
			"Cannot uninstall the app because it contain data, if you want to go further first cancel the document."
		)
	else:
		return "No submitted "


def extend_bootinfo(bootinfo):
	settings = frappe.get_single("QuickFix Settings")

	bootinfo.quickfix_shop_name = settings.shop_name
	bootinfo.quickfix_manager_email = settings.manager_email


def session_creation(login_manager):
	frappe.log_error(title="User Login", message=f"{frappe.session.user} logged in to the page")


def session_logout(login_manager):
	frappe.log_error(title="User logged out", message=f"{frappe.session.user} logged out")


def fixtures():
	frappe.make_property_setter(
		{
			"doctype": "Job Card",
			"fieldname": "remarks",
			"property": "bold",
			"value": "1",
			"property_type": "Check",
		}
	)


class TestGetCountOverride(FrappeTestCase):
	def test_override_is_called(self):
		"""Confirm override runs by checking Audit Log entry"""
		frappe.call("frappe.client.get_count", doctype="User")

		log = frappe.get_all("Audit Log", filters={"doctype_name": "User", "action": "count_queried"})

		self.assertTrue(len(log) > 0)

	def test_original_logic_returns_correct_count(self):
		"""Confirm original count logic still works"""
		expected = frappe.db.count("User")

		result = frappe.call("frappe.client.get_count", doctype="User")

		self.assertEqual(result, expected)

	def test_other_calls_not_broken(self):
		"""Confirm override does not break other calls"""
		result = frappe.call("frappe.client.get_count", doctype="Role")

		self.assertIsInstance(result, int)
