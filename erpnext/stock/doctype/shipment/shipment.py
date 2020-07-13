# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import requests
import re
from frappe import _
from frappe.model.document import Document
from erpnext.accounts.party import get_party_shipping_address
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe.contacts.doctype.address.address import get_address_display
from frappe.utils import today


class Shipment(Document):
	def validate(self):
		self.validate_weight()
		if self.docstatus == 0:
			self.status = 'Draft'

	def on_submit(self):
		if not self.shipment_parcel:
			frappe.throw(_('Please enter Shipment Parcel information'))
		if self.value_of_goods == 0:
			frappe.throw(_('Value of goods cannot be 0'))
		self.status = 'Submitted'

	def on_cancel(self):
		self.status = 'Cancelled'

	def validate_weight(self):
		for parcel in self.shipment_parcel:
			if parcel.weight <= 0:
				frappe.throw(_('Parcel weight cannot be 0'))

@frappe.whitelist()
def get_address_name(ref_doctype, docname):
	""" Return address name """
	return get_party_shipping_address(ref_doctype, docname)

@frappe.whitelist()
def get_contact_name(ref_doctype, docname):
	""" Return address name """
	return get_default_contact(ref_doctype, docname)
