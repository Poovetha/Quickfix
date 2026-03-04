// Copyright (c) 2026, quickfix and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Card", {
	refresh(frm) {
		frm.set_query("assigned__technician", () => {
			return {
				filters: {
					specialization: frm.doc.device_type,
					status: "Active",
				},
			};
		});
		if (frm.doc.status === "Draft") {
			frm.dashboard.add_indicator(frm.doc.status, "grey");
		} else if (frm.doc.status === "Pending Diagnosis") {
			frm.dashboard.add_indicator(frm.doc.status, "orange");
		} else if (frm.doc.status === "Awaiting Customer Approval") {
			frm.dashboard.add_indicator(frm.doc.status, "yellow");
		} else if (frm.doc.status === "In Repair") {
			frm.dashboard.add_indicator(frm.doc.status, "blue");
		} else if (frm.doc.status === "Ready for Delivery") {
			frm.dashboard.add_indicator(frm.doc.status, "green");
		} else if (frm.doc.status === "Delivered") {
			frm.dashboard.add_indicator(frm.doc.status, "green");
		} else if (frm.doc.status === "Cancelled") {
			frm.dashboard.add_indicator(frm.doc.status, "red");
		}

		if (frm.doc.status === "Ready for Delivery" && frm.doc.docstatus === 1) {
			frm.add_custom_button("Mark as Delivered", function () {
				frm.set_value("status", "Delivered");
				frm.save();
				frappe.show_alert({
					message: "Status Changed to Delivered",
					indicator: "blue",
				});
			});
		}

		if (frappe.boot.quickfix_shop_name) {
			frm.page.set_title(frappe.boot.quickfix_shop_name);
		}
	},
});
frappe.realtime.on("job_ready", (data) => {
	frappe.show_progress("Job Status", 100, 100, "Completing");
});
