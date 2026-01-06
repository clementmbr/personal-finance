# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    category_id = fields.Many2one(
        comodel_name="bank.statement.line.category",
        string="Category",
        domain="[('parent_id', '=', False)]",
        compute="_compute_category_id",
        readonly=False,
        store=True,
    )
    category_color = fields.Integer(
        related="category_id.color",
        string="Color",
        store=True,
    )
    subcategory_id = fields.Many2one(
        comodel_name="bank.statement.line.category",
        string="Sub-Category",
        domain="[('parent_id', '=', category_id)]",
    )
    is_expense = fields.Boolean(
        related="category_id.is_expense",
        store=True,
        string="Is Expense",
    )

    @api.depends("subcategory_id")
    def _compute_category_id(self):
        for line in self:
            line.category_id = line.subcategory_id.parent_id
