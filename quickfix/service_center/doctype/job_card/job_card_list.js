frappe.listview_settings["Job Card"] = {
	add_fields: ["status", "customer_name", "final_amount", "priority"],
	has_indicator_for_draft: true,

	get_indicator(doc) {
		if (doc.status == "In Repair") {
			return ["In Repair", "orange", "status,=,In Repair"];
		} else if (doc.status == "Delivered") {
			return ["Delivered", "green", "status,=,Delivered"];
		} else if (doc.status == "Cancelled") {
			return ["Cancelled", "red", "status,=,Cancelled"];
		} else if (doc.status == "Ready for Delivery") {
			return ["Ready for Delivery", "blue", "status,=,Ready for Delivery"];
		}
	},

	formatters: {
		final_amount(value) {
			if (!value) return "";
			return format_currency(value, "INR");
		},
	},

	button: {
		show(doc) {
			return doc.status === "In Repair";
		},
		get_label() {
			return "Mark Completed";
		},
		get_description(doc) {
			return __("View {0}", [`${doc.status}`]);
		},
		action(doc) {
			frappe.call({
				method: "frappe.client.set_value",
				args: {
					doctype: "Job Card",
					name: doc.name,
					fieldname: "status",
					value: "Completed",
				},
				callback() {
					frappe.listview.refresh();
				},
			});
		},
	},
};
