# Copyright 2026 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountStatementLineMassUpdate(models.TransientModel):
    _name = "account.statement.line.mass.update"
    _description = "Mass Update Category"

    category_id = fields.Many2one("bank.statement.line.category")
    subcategory_id = fields.Many2one(
        "bank.statement.line.category", domain=[("parent_id", "=", "category_id")]
    )
    line_ids = fields.Many2many(
        "account.bank.statement.line",
        string="Lines to Update",
        relation="category_statement_line_rel",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Pre-fill lines based on selection in the list view
        if self.env.context.get("active_model") == "account.bank.statement.line":
            active_ids = self.env.context.get("active_ids", [])
            res["line_ids"] = [(6, 0, active_ids)]
        return res

    def action_apply(self):
        self.ensure_one()
        vals = {
            "category_id": self.category_id.id,
            "subcategory_id": self.subcategory_id.id,
        }
        self.line_ids.write(vals)
        return {"type": "ir.actions.act_window_close"}
