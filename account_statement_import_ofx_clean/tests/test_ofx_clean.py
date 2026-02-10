import base64
import datetime

import odoo.tests.common as common
from odoo.tools import file_open


class TestOfxFile(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.asi_model = cls.env["account.statement.import"]
        cls.abs_model = cls.env["account.bank.statement"]
        cls.absl_model = cls.env["account.bank.statement.line"]
        cur = cls.env.ref("base.USD")
        bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "123456",
                "partner_id": cls.env.ref("base.main_partner").id,
                "company_id": cls.env.ref("base.main_company").id,
                "bank_id": cls.env.ref("base.res_bank_1").id,
            }
        )
        cls.env["account.journal"].create(
            {
                "name": "Bank Journal TEST OFX",
                "code": "BNK12",
                "type": "bank",
                "bank_account_id": bank.id,
                "currency_id": cur.id,
            }
        )

    def test_clean_ofx_file_import(self):
        ofx_path = "account_statement_import_ofx_clean/tests/test_ofx_clean.ofx"
        with file_open(ofx_path, "rb") as ofx_file:
            ofx_bin = ofx_file.read()
            wizard = self.asi_model.create(
                {
                    "statement_file": base64.b64encode(ofx_bin),
                    "statement_filename": "test_ofx.ofx",
                    "clean_ofx_file": True,
                }
            )
            wizard.import_file_button()
            bank_st_record = self.abs_model.search([("name", "like", "123456")])[0]
            self.assertEqual(bank_st_record.balance_start, 2516.56)
            self.assertEqual(bank_st_record.balance_end_real, 2156.56)

            line = self.absl_model.search(
                [
                    ("payment_ref", "=", "Agrolait"),
                    ("statement_id", "=", bank_st_record.id),
                ]
            )[0]
            self.assertEqual(line.date, datetime.date(2013, 8, 24))
