import frappe
import frappe.utils as fu

from quickfix.monkey_patch import apply_all


class TestGetUrl:
	def setup_method(self):
		apply_all()

	def test_with_prefix(self):
		frappe.conf.custom_url_prefix = "https://cdn.example.com"

		url = fu.get_url("/files/test.png")

		assert "https://cdn.example.com" in url

	def test_without_prefix(self):
		frappe.conf.custom_url_prefix = ""

		url = fu.get_url("/files/test.png")

		# Should behave like original
		assert "/files/test.png" in url
