# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from datetime import date

from odoo import Command
from odoo.tests.common import TransactionCase


class TestAccountStatementReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.eur = self.env.ref("base.EUR")
        self.brl = self.env.ref("base.BRL")
        self.brl.active = True
        self.eur.active = True
        self.company = self.env.company

        # 1. Create BRL Journal
        self.journal_brl = self.env["account.journal"].create(
            {
                "name": "BRL Bank",
                "type": "bank",
                "code": "BRL01",
                "currency_id": self.brl.id,
            }
        )

        # 2. Setup Rates (BRL rate changes in March)
        self.env["res.currency.rate"].create(
            [
                {
                    "name": "2025-01-01",
                    "rate": 1.0,
                    "currency_id": self.eur.id,
                    "company_id": self.company.id,
                },
                {
                    "name": "2025-01-01",
                    "rate": 5.0,
                    "currency_id": self.brl.id,
                    "company_id": self.company.id,
                },
                {
                    "name": "2025-03-01",
                    "rate": 6.0,
                    "currency_id": self.brl.id,
                    "company_id": self.company.id,
                },
            ]
        )

        # 3. Create Statement with lines (Jan and March)
        self.statement = self.env["account.bank.statement"].create(
            {
                "name": "Test Statement 2024",
                "line_ids": [
                    Command.create(
                        {
                            "date": "2025-01-15",
                            "amount": 100.0,
                            "payment_ref": "Opening",
                            "journal_id": self.journal_brl.id,
                        }
                    ),
                    Command.create(
                        {
                            "date": "2025-03-10",
                            "amount": 50.0,
                            "payment_ref": "March Deposit",
                            "journal_id": self.journal_brl.id,
                        }
                    ),
                ],
            }
        )

    def test_report_propagation(self):
        self.statement.line_ids._compute_running_balance()
        self.env.invalidate_all()

        results = self.env["account.statement.balance.report"].search(
            [("journal_id", "=", self.journal_brl.id)], order="date asc"
        )

        nov = results.filtered(lambda r: r.date == date(2024, 11, 30))
        jan = results.filtered(lambda r: r.date == date(2025, 1, 31))
        feb = results.filtered(lambda r: r.date == date(2025, 2, 28))
        mar = results.filtered(lambda r: r.date == date(2025, 3, 31))

        self.assertEqual(nov.balance, 0)

        # Jan: 100 BRL / 5.0 = 20 EUR
        self.assertEqual(jan.balance, 100.0)
        self.assertEqual(jan.balance_eur, 20.0)

        # Feb: Propagated 100 BRL / 5.0 (still Jan rate) = 20 EUR
        self.assertEqual(feb.balance, 100.0)
        self.assertEqual(feb.balance_eur, 20.0)

        # Mar: 150 BRL (100+50) / 6.0 = 25 EUR
        self.assertEqual(mar.balance, 150.0)
        self.assertEqual(mar.balance_eur, 25.0)
