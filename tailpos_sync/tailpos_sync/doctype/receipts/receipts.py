# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from tailpos_sync.utils import set_date_updated

import uuid


class Receipts(Document):
	def autoname(self):
		if not self.id:
			self.id = 'Receipt/' + str(uuid.uuid4())
		self.name = self.id


	def set_total_amount(self):
		self.total_amount = 0

	def set_default_values(self):
		"""Set the status as title-d form"""
		self.status = self.status.title()
		self.series = 'Receipt/{0}'.format(self.receiptnumber)
		self.set_total_amount()

	def before_insert(self):
		"""Setup the Receipts document"""
		self.set_default_values()

	def compute_total(self):
		total = (float(self.subtotal) + float(self.taxesvalue)) - float(self.discount_amount)
		if self.loyalty_type == "Redeemed":
			total -= int(self.loyalty_points)
		if self.roundoff:
			remainder = float(total) % int(total)
			print(remainder)
			if remainder > 0.05:
				total = int(total) + 1
			else:
				total = int(total)
		self.total_amount = total

	def compute_subtotal(self):
		subtotal = 0
		for item in self.receipt_lines:
			subtotal += (float(item.__dict__['qty']) * float(item.__dict__['price']))
		self.subtotal = subtotal

	def compute_total_tax(self):
		taxes = 0
		for tax in self.receipt_taxes:
			taxes += float(tax.__dict__['amount'])
		self.taxesvalue = taxes

	def compute_discount(self):
		if self.discounttype == "Percentage":
			self.discount_amount = round((float(self.discountvalue)/100) * self.subtotal,2)
		else:
			self.discount_amount = self.discountvalue
	def validate(self):
		set_date_updated(self)
		self.status = "Completed"
		self.compute_subtotal()
		self.compute_discount()
		self.compute_total_tax()
		self.compute_total()
