# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def action_compute_journals_current_balance(self):
        """Action to trigger balance recomputation for selected journals."""
        self._compute_current_statement_balance()

    def action_compute_lines_running_balance(self):
        """Action to trigger running balance recomputation for all the statement lines
        from the selected journals."""
        for rec in self:
            lines = self.env["account.bank.statement.line"].search(
                [("journal_id", "=", rec.id)], order="internal_index asc"
            )
            self.env.add_to_compute(lines._fields["running_balance"], lines)
            lines.flush_model(["running_balance"])
