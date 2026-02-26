// Copyright (c) 2026, quickfix and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Card", {
	refresh(frm) {},
});

frappe.realtime.on("job_ready", (data) => {
	frappe.msgprint("Your job is ready!");
});
