import frappe
from frappe.tests.utils import FrappeTestCase


class test_override(FrappeTestCase):
	def override_called(self):  # Confirm override runs by checking Audit Log entry
		frappe.call("frappe.client.get_count", doctype="User")
		log = frappe.get_all("Audit Log", filters={"doctype_name": "User", "action": "count_queried"})
		self.assertTrue(len(log) > 0)

	def returns_correct_count(self):  # Confirm original count logic still works
		count = frappe.db.count("User")
		result = frappe.call("frappe.client.get_count", doctype="User")
		self.assertEqual(result, count)

	def other_not_broken(self):  # Confirm override does not break other calls
		result = frappe.call("frappe.client.get_count", doctype="Role")
		self.assertIsInstance(result, int)
