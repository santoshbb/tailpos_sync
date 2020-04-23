# Copyright (c) 2013, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	cost_center = filters.get("cost_center")

	if from_date > to_date:
		frappe.throw("From Date should be before To Date")
	else:
		columns.append({"fieldname": "store_name", "label": "Store Name", "fieldtype": "Data", "width": 150})
		columns.append({"fieldname": "discount", "label": "Discount", "fieldtype": "Data", "width": 100})
		columns.append({"fieldname": "net_sale", "label": "Net Sale", "fieldtype": "Data", "width": 100})
		columns.append({"fieldname": "vat", "label": "VAT", "fieldtype": "Data", "width": 100})
		columns.append({"fieldname": "gross_sale", "label": "Gross Sale", "fieldtype": "Data", "width": 100})

		query = """ SELECT * FROM `tabSales Invoice` 
				WHERE docstatus=1 and posting_date BETWEEN '{0}' and '{1}' and cost_center = '{2}'""".format(from_date, to_date,cost_center)
		print(query)
		sales_invoices = frappe.db.sql(query, as_dict=True)

		for i in sales_invoices:
			obj = {
				"store_name": i.pos_profile,
				"discount": i.discount_amount,
				"net_sale": i.total,
				"gross_sale": i.grand_total,
				"vat": i.total_taxes_and_charges,
			}
			mode_of_payments = frappe.db.sql(""" SELECT * FROM `tabSales Invoice Payment` WHERE parent=%s """,i.name,as_dict=True)
			for ii in mode_of_payments:
				check_mop(columns,ii)
				obj[ii.mode_of_payment] = ii.amount

			data.append(obj)


	return columns, data

def check_mop(columns, ii):
	add = True
	for i in columns:
		if i.get("label") == ii.mode_of_payment:
			add = False
	if add:
		columns.append({
			"fieldname": ii.mode_of_payment,
			"label": ii.mode_of_payment,
			"fieldtype": "Data",
			"width": 150
		})