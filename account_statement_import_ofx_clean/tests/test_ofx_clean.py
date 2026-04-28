import base64

from odoo.tests.common import TransactionCase
from odoo.tools import file_open


class TestOfxClean(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_model = cls.env["account.statement.import"]

        # Ensure USD currency is active
        usd_curr = cls.env.ref("base.USD")
        usd_curr.write({"active": True})

        # Setup Bank Account and Journal in USD
        cls.bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "TEST_USD_123",
                "partner_id": cls.env.ref("base.main_partner").id,
                "currency_id": usd_curr.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Bank USD Test",
                "code": "BUSD",
                "type": "bank",
                "bank_account_id": cls.bank.id,
                "currency_id": usd_curr.id,
                "ignore_empty_fitid": True,
                "deduplicate_fitid_by_amount": True,
            }
        )

    def test_01_ignore_empty_fitid(self):
        """Verify that the transaction with empty FITID is filtered out"""
        path = "account_statement_import_ofx_clean/tests/test_empty_fitid.ofx"
        with file_open(path, "rb") as f:
            content = f.read()

        wizard = self.wizard_model.create(
            {
                "statement_file": base64.b64encode(content),
                "statement_filename": "empty.ofx",
            }
        )
        wizard.import_file_button()

        statement = self.env["account.bank.statement"].search(
            [("name", "=", "TEST_USD_123")], limit=1
        )
        # Should only have 1 line (the one with FITID 'VALID1')
        self.assertEqual(len(statement.line_ids), 1)
        self.assertEqual(statement.line_ids.payment_ref, "Valid Tx")

    def test_02_deduplicate_fitid_by_amount(self):
        """Verify that duplicates FITID with different amounts are imported"""
        path = "account_statement_import_ofx_clean/tests/test_duplicated_fitid.ofx"
        with file_open(path, "rb") as f:
            content = f.read()

        wizard = self.wizard_model.create(
            {
                "statement_file": base64.b64encode(content),
                "statement_filename": "dup.ofx",
            }
        )
        # This triggers the cleaning and then the standard Odoo import
        wizard.import_file_button()

        statement = self.env["account.bank.statement"].search(
            [("name", "=", "TEST_USD_123")], limit=1
        )
        # All the lines should be present
        self.assertEqual(
            len(statement.line_ids), 4, "Duplicate FITID should have been handled"
        )
