# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class BankStatementLineCategory(models.Model):
    _name = "bank.statement.line.category"
    _description = "Bank Statement Line Category"
    _order = "sequence, is_expense desc, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer()
    is_expense = fields.Boolean(
        default=True, help="Check for expenses, uncheck for revenues."
    )
    parent_id = fields.Many2one(
        comodel_name="bank.statement.line.category",
        string="Parent Category",
        ondelete="cascade",
    )
    child_ids = fields.One2many(
        comodel_name="bank.statement.line.category",
        inverse_name="parent_id",
        string="Sub-categories",
    )

    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.parent_id:
                name = f"{record.parent_id.name} / {name}"
            result.append((record.id, name))
        return result
