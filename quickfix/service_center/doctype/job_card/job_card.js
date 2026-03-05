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

		if (frm.doc.docstatus == 1) {
			console.log("sdfghjk");
			frm.add_custom_button("Reject Job", () => {
				let d = new frappe.ui.Dialog({
					title: "Reject Job",
					fields: [
						{
							label: "Rejection Reason",
							fieldname: "reason",
							fieldtype: "Small Text",
							reqd: 1,
						},
					],
					primary_action_label: "Submit",
					primary_action(values) {
						frm.set_value("status", "Cancelled");
						frm.save();
						d.hide();
					},
				});
				d.show();
			});
		}
		frm.add_custom_button("Transfer Technician", () => {
			frappe.prompt(
				[
					{
						label: "New Technician",
						fieldname: "technician",
						fieldtype: "Link",
						options: "User",
						reqd: 1,
					},
				],
				function (values) {
					frappe.confirm(
						"Are you sure you want to transfer this job to another technician?",
						function () {
							frappe.call({
								method: "quickfix.job_card.transfer_technician",
								args: {
									job_card: frm.doc.name,
									technician: values.technician,
								},
								callback: function (r) {
									if (!r.exc) {
										frappe.msgprint("Technician transferred successfully");
										frm.set_value("assigned__technician", values.technician);
										frm.trigger("assigned__technician");
										frm.reload_doc();
									}
								},
							});
						}
					);
				}
			);
		});

		if (!frappe.user.has_role("Manager")) {
			frm.set_df_property("customer_phone", "hidden", 1);
		}
	},
	status(frm) {
		if (frm.doc.status == "Delivered") {
			frappe.show_alert("Delivered");
		}
	},

	assigned__technician(frm) {
		if (!frm.doc.assigned__technician) return;
		frappe.db
			.get_value("Technician", frm.doc.assigned__technician, "specialization")
			.then((r) => {
				if (r.message.specialization !== frm.doc.device_type) {
					frappe.msgprint("Technician specialization does not match the device type.");
				}
			});
	},

	onload(frm) {
		frappe.realtime.on("job_ready", function (data) {
			frappe.show_alert({
				message: "Job is Ready!",
				indicator: "green",
			});
		});
	},
});

frappe.ui.form.on("Part Used", {
	quantity(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "total_price", row.quantity * row.unit_price);
	},
});
