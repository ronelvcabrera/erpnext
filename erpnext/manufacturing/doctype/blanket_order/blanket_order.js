// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Blanket Order", {
  onload: function(frm) {
    frm.trigger("set_tc_name_filter");
  },
  setup: function(frm) {
    frm.add_fetch("customer", "customer_name", "customer_name");
    frm.add_fetch("supplier", "supplier_name", "supplier_name");
  },
  customer: function(frm) {
    erpnext.utils.get_party_details(frm);
  },
  supplier: function(frm) {
    erpnext.utils.get_party_details(frm);
  },
  customer_address: function(frm) {
    erpnext.utils.get_address_display(
      frm,
      "customer_address",
      "address_display"
    );
  },
  supplier_address: function(frm) {
    erpnext.utils.get_address_display(
      frm,
      "supplier_address",
      "address_display"
    );
  },
  contact_person: function(frm) {
    erpnext.utils.get_contact_details(frm);
  },
  company: function(frm) {
    frm.set_value("currency", erpnext.get_currency(frm.doc.company));
  },
  refresh: function(frm) {
    frm.events.set_dynamic_labels(frm);
    if (frm.doc.customer && frm.doc.docstatus === 1) {
      frm.add_custom_button(__("View Orders"), function() {
        frappe.set_route("List", "Sales Order", {
          blanket_order: frm.doc.name
        });
      });
      frm
        .add_custom_button(__("Create Sales Order"), function() {
          frappe.model.open_mapped_doc({
            method:
              "erpnext.manufacturing.doctype.blanket_order.blanket_order.make_sales_order",
            frm: frm
          });
        })
        .addClass("btn-primary");
    }

    if (frm.doc.supplier && frm.doc.docstatus === 1) {
      frm.add_custom_button(__("View Orders"), function() {
        frappe.set_route("List", "Purchase Order", {
          blanket_order: frm.doc.name
        });
      });
      frm
        .add_custom_button(__("Create Purchase Order"), function() {
          frappe.model.open_mapped_doc({
            method:
              "erpnext.manufacturing.doctype.blanket_order.blanket_order.make_purchase_order",
            frm: frm
          });
        })
        .addClass("btn-primary");
    }
  },

  refresh: function(frm) {
    erpnext.hide_company();
    if (frm.doc.customer && frm.doc.docstatus === 1) {
      frm.add_custom_button(__("View Orders"), function() {
        frappe.set_route("List", "Sales Order", {
          blanket_order: frm.doc.name
        });
      });
      frm
        .add_custom_button(__("Create Sales Order"), function() {
          frappe.model.open_mapped_doc({
            method:
              "erpnext.manufacturing.doctype.blanket_order.blanket_order.make_sales_order",
            frm: frm
          });
        })
        .addClass("btn-primary");
    }
  },
  tc_name: function(frm) {
    erpnext.utils.get_terms(frm.doc.tc_name, frm.doc, function(r) {
      if (!r.exc) {
        frm.set_value("terms", r.message);
      }
    });
  },
  set_dynamic_labels: function(frm) {
    var company_currency = erpnext.get_currency(frm.doc.company);
    cur_frm.set_df_property(
      "conversion_rate",
      "description",
      "1 " + frm.doc.currency + " = [?] " + company_currency
    );
    frm.set_currency_labels(["rate"], frm.doc.currency, "items");
  },
  currency: function(frm) {
    var company_currency = erpnext.get_currency(frm.doc.company);
    var args;
    if (frm.doc.blanket_order_type == "Selling") {
      args = "for_selling";
    } else {
      args = "for_buying";
    }
    return frappe.call({
      method: "erpnext.setup.utils.get_exchange_rate",
      args: {
        transaction_date: frm.doc.posting_date,
        from_currency: frm.doc.currency,
        to_currency: company_currency,
        args: args
      },
      callback: function(r) {
        frm.set_value("conversion_rate", flt(r.message));
        frm.events.set_dynamic_labels(frm);
      }
    });
  },

  onload_post_render: function(frm) {
    frm.get_field("items").grid.set_multiple_add("item_code", "qty");
  },

  set_tc_name_filter: function(frm) {
    if (frm.doc.blanket_order_type === "Selling") {
      frm.set_df_property("customer", "reqd", 1);
      frm.set_df_property("supplier", "reqd", 0);
      frm.set_value("supplier", "");

      frm.set_query("tc_name", function() {
        return { filters: { selling: 1 } };
      });
    }
    if (frm.doc.blanket_order_type === "Purchasing") {
      frm.set_df_property("supplier", "reqd", 1);
      frm.set_df_property("customer", "reqd", 0);
      frm.set_value("customer", "");

      frm.set_query("tc_name", function() {
        return { filters: { buying: 1 } };
      });
    }
  },

  blanket_order_type: function(frm) {
    frm.trigger("set_tc_name_filter");
  }
});

frappe.ui.form.on("Blanket Order Item", {
  rate: function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    frappe.model.set_value(
      cdt,
      cdn,
      "base_rate",
      d.rate * frm.doc.conversion_rate
    );
  }
});
