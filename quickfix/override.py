import frappe

from quickfix.service_center.doctype.job_card.job_card import JobCard


class CustomJobCard(JobCard):
	def validate(self):
		super().validate()  # Always call super first
		self._check_urgent_unassigned()
		# if we want to run the custom function first the call must in order.

	def _check_urgent_unassigned(self):
		if self.priority == "Urgent" and not self.assigned_technician:
			settings = frappe.get_single("QuickFix Settings")
			frappe.enqueue(
				"quickfix.utils.send_urgent_alert", job_card=self.name, manager=settings.manager_email
			)


# What is Method Resolution Order (MRO)?
# It is a feature by which can define execution order by how in parent class define.
# CustomJobCard -> JobCard -> Document -> BaseDocument -> object

# why calling super() is non-negotiable
#     super().validate() ensures the original validation for doctype runs before your custom logic.


# when would you choose override_doctype class over doc_events?
# Use override_doctype_class when you need to change or extend the core validation
# of a DocType (like validate, save, submit logic).

# Use doc_events only want to react to events like after_submit, before_submit,etc..
# which used to  send email, log activity without altering core behavior.
# choose to use override because here need to extend the validation using super().validate()
