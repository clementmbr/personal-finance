# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests.common import TransactionCase
from datetime import date


class TestAccountStatementReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.eur = self.env.ref("base.EUR")
        self.brl = self.env.ref("base.BRL")
        self.brl.active = True
        self.company = self.env.company
        self.journal_brl = self.env["account.journal"].create(
            {
                "name": "BRL Bank",
                "type": "bank",
                "code": "BRL01",
                "currency_id": self.brl.id,
            }
        )
        self.env["res.currency.rate"].create(
            [
                {
                    "name": "2024-01-01",
                    "rate": 1.0,
                    "currency_id": self.eur.id,
                    "company_id": self.company.id,
                },
                {
                    "name": "2024-01-01",
                    "rate": 5.0,
                    "currency_id": self.brl.id,
                    "company_id": self.company.id,
                },
                {
                    "name": "2024-03-01",
                    "rate": 6.0,
                    "currency_id": self.brl.id,
                    "company_id": self.company.id,
                },
            ]
        )

    def _create_statement_line(self, amount, date_str):
        line = self.env["account.bank.statement.line"].create(
            {
                "date": date_str,
                "journal_id": self.journal_brl.id,
                "amount": amount,
                "payment_ref": "Test",
            }
        )
        line.move_id.action_post()
        return line

    def test_report_propagation(self):
        self._create_statement_line(100, "2024-01-15")
        self._create_statement_line(50, "2024-03-10")
        results = self.env["account.statement.balance.report"].search(
            [("journal_id", "=", self.journal_brl.id)], order="date asc"
        )
        jan = results.filtered(lambda r: r.date == date(2024, 1, 31))
        feb = results.filtered(lambda r: r.date == date(2024, 2, 29))
        mar = results.filtered(lambda r: r.date == date(2024, 3, 31))
        self.assertEqual(jan.balance, 100.0)
        self.assertEqual(jan.balance_eur, 20.0)
        self.assertEqual(feb.balance, 100.0)
        self.assertEqual(mar.balance, 150.0)
        self.assertEqual(mar.balance_eur, 25.0)
