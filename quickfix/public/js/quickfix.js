frappe.ready(function () {
	const shopName = frappe.boot.quickfix_shop_name;

	if (shopName) {
		$(".navbar-home").append(
			`<span style="margin-left:15px;font-weight:600;">
                ${shopName}
            </span>`
		);
	}
});
