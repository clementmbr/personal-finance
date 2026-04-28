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
    category_background_color = fields.Char(related="category_id.background_color")
    category_text_color = fields.Char(related="category_id.text_color")
    subcategory_id = fields.Many2one(
        comodel_name="bank.statement.line.category",
        string="Sub-Category",
        domain="[('parent_id', '=', category_id)]",
    )
    category_type = fields.Selection(related="category_id.category_type", store=True)
    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account")
    note = fields.Text(help="Personal notes")

    @api.depends("subcategory_id")
    def _compute_category_id(self):
        for line in self:
            line.category_id = line.subcategory_id.parent_id

    @api.model_create_multi
    def create(self, vals_list):
        """Auto fill category for statement lines with the same label"""
        for vals in vals_list:
            if vals.get("category_id"):
                continue

            label = vals.get("payment_ref")
            if label:
                past_line = self.search(
                    [("payment_ref", "=", label), ("category_id", "!=", False)],
                    limit=1,
                    order="date desc, id desc",
                )

                if past_line:
                    vals["category_id"] = past_line.category_id.id
                    vals["subcategory_id"] = past_line.subcategory_id.id

        return super().create(vals_list)
