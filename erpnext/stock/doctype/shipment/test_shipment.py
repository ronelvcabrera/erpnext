# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals
import json

import frappe
import unittest
from erpnext.stock.doctype.shipment.shipment import fetch_shipping_rates
from erpnext.stock.doctype.shipment.shipment import create_shipment
from erpnext.stock.doctype.shipment.shipment import update_tracking

class TestShipment(unittest.TestCase):
	pass

	def test_shipment_booking(self):
		shipment = create_test_shipment()
		try:
			shipment.submit()
		except:
			frappe.throw('Error occurred on submit shipment')
		shipment_parcel = convert_shipmet_parcel(shipment.shipment_parcel)
		shipment_rates = fetch_shipping_rates(shipment.pickup_from_type, shipment.delivery_to_type, 
			shipment.pickup_address_name, shipment.delivery_address_name,
			shipment_parcel, shipment.description_of_content,
			shipment.pickup_date, shipment.value_of_goods,
			pickup_contact_name=shipment.pickup_contact_name,
			delivery_contact_name=shipment.delivery_contact_name
		)
		if len(shipment_rates) > 0:
			# We are taking the first shipment rate
			rate = shipment_rates[0]
			new_shipment = create_shipment(
				shipment=shipment.name,
				pickup_from_type=shipment.pickup_from_type,
				delivery_to_type=shipment.delivery_to_type,
				pickup_address_name=shipment.pickup_address_name,
				delivery_address_name=shipment.delivery_address_name,
				shipment_parcel=shipment_parcel,
				description_of_content=shipment.description_of_content,
				pickup_date=shipment.pickup_date,
				pickup_contact_name=shipment.pickup_contact_name,
				delivery_contact_name=shipment.delivery_contact_name,
				value_of_goods=shipment.value_of_goods,
				service_data=json.dumps(rate),
				shipment_notific_email=None,
				tracking_notific_email=None,
				delivery_notes=None
			)
			service_provider = rate.get('service_provider')
			shipment_id = new_shipment.get('shipment_id')
			tracking_data = update_tracking(
				shipment.name,
				service_provider,
				shipment_id,
				delivery_notes=None
			)
			doc = frappe.get_doc('Shipment', shipment.name)
			self.assertEqual(doc.service_provider, rate.get('service_provider'))
			self.assertEqual(doc.shipment_amount, rate.get('actual_price'))
			self.assertEqual(doc.carrier, rate.get('carrier'))
			self.assertEqual(doc.tracking_status, tracking_data.get('tracking_status'))
			self.assertEqual(doc.tracking_url, tracking_data.get('tracking_url'))


def create_test_shipment():
	company = get_shipment_company()
	company_address = get_shipment_company_address(company.name)
	customer = get_shipment_customer()
	customer_address = get_shipment_customer_address(customer.name)
	customer_contact = get_shipment_customer_contact(customer.name)

	shipment = frappe.new_doc("Shipment")
	shipment.pickup_from_type = 'Company'
	shipment.pickup_company = company.name
	shipment.pickup_address_name = company_address.name
	shipment.delivery_to_type = 'Customer'
	shipment.delivery_customer = customer.name
	shipment.delivery_address_name = customer_address.name
	shipment.delivery_contact_name = customer_contact.name
	shipment.pallets = 'No'
	shipment.shipment_type = 'Goods'
	shipment.value_of_goods = 1000
	shipment.pickup_type = 'Pickup'
	shipment.pickup_date = '2020-07-29'
	shipment.pickup_from = '09:00'
	shipment.pickup_to = '17:00'
	shipment.description_of_content = 'unit test entry'
	shipment.append('shipment_parcel',
		{
			"length": 5,
			"width": 5,
			"height": 5,
			"weight": 5,
			"count": 5
		}
	)
	shipment.insert()
	frappe.db.commit()
	return shipment


def get_shipment_customer_contact(customer_name):
	contact_fname = 'Customer Shipment'
	contact_lname = 'Testing'
	customer_name = contact_fname + ' ' + contact_lname
	contacts = frappe.get_all("Contact", fields=["name"], filters = {"name": customer_name})
	if len(contacts):
		return contacts[0]
	else:
		return create_customer_contact(contact_fname, contact_lname)


def get_shipment_customer_address(customer_name):
	address_title = customer_name + ' address 123'
	customer_address = frappe.get_all("Address", fields=["name"], filters = {"address_title": address_title})
	if len(customer_address):
		return customer_address[0]
	else:
		return create_shipment_address(address_title, customer_name, 81929)

def get_shipment_customer():
	customer_name = 'Shipment Customer'
	customer = frappe.get_all("Customer", fields=["name"], filters = {"name": customer_name})
	if len(customer):
		return customer[0]
	else:
		return create_shipment_customer(customer_name)

def get_shipment_company_address(company_name):
	address_title = company_name + ' address 123'
	addresses = frappe.get_all("Address", fields=["name"], filters = {"address_title": address_title})
	if len(addresses):
		return addresses[0]
	else:
		return create_shipment_address(address_title, company_name, 80331)

def get_shipment_company():
	company_name = 'Shipment Company'
	abbr = 'SC'
	companies = frappe.get_all("Company", fields=["name"], filters = {"company_name": company_name})
	if len(companies):
		return companies[0]
	else:
		return create_shipment_company(company_name, abbr)

def create_shipment_address(address_title, company_name, postal_code):
	address = frappe.new_doc("Address")
	address.address_title = address_title
	address.address_type = 'Shipping'
	address.address_line1 = company_name + ' address line 1'
	address.city = 'Random City'
	address.postal_code = postal_code
	address.country = 'Germany'
	address.insert()
	return address


def create_customer_contact(fname, lname):
	customer = frappe.new_doc("Contact")
	customer.customer_name = fname + ' ' + lname
	customer.first_name = fname
	customer.last_name = lname
	customer.is_primary_contact = 1
	customer.is_billing_contact = 1
	customer.append('email_ids',
		{
			'email_id': 'randomme@email.com',
			'is_primary': 1
		}
	)
	customer.append('phone_nos',
		{
			'phone': '123123123',
			'is_primary_phone': 1,
			'is_primary_mobile_no': 1
		}
	)
	customer.status = 'Passive'
	customer.insert()
	return customer


def create_shipment_company(company_name, abbr):
	company = frappe.new_doc("Company")
	company.company_name = company_name
	company.abbr = abbr
	company.default_currency = 'EUR'
	company.country = 'Germany'
	company.insert()
	return company

def create_shipment_customer(customer_name):
	customer = frappe.new_doc("Customer")
	customer.customer_name = customer_name
	customer.customer_type = 'Company'
	customer.customer_group = 'All Customer Groups'
	customer.territory = 'All Territories'
	customer.gst_category = 'Unregistered'
	customer.insert()
	return customer

def convert_shipmet_parcel(shipmet_parcel):
	data = []
	for parcel in shipmet_parcel:
		data.append(
			{
				"length": parcel.length,
				"width": parcel.width,
				"height": parcel.height,
				"weight": parcel.weight,
				"count": parcel.count
			}
		)
	return json.dumps(data)
