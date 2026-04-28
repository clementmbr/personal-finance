# Copyright 2026 Akretion France (http://www.akretion.com/)
import logging
import re

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AccountStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    remove_empty_fitid = fields.Boolean(
        string="Remove empty FITID",
        help="Remove <STMTTRN> blocks with empty FITID (common in Banco do Brasil).",
    )
    deduplicate_fitid_by_amount = fields.Boolean(
        string="Deduplicate FITID by amount",
        help="Append transaction amount and sign to FITID to allow importing "
        "duplicated IDs with different amounts or signs (useful for Nubank IOF "
        "and refunds).",
    )

    def _parse_file(self, data_file):
        if data_file and (self.remove_empty_fitid or self.deduplicate_fitid_by_amount):
            try:
                content = data_file.decode("utf-8")
            except UnicodeDecodeError:
                content = data_file.decode("latin-1")

            def _process_block(match):
                block = match.group(0)

                if self.remove_empty_fitid:
                    if re.search(r"<FITID>\s*</FITID>", block, flags=re.DOTALL):
                        return ""

                if self.deduplicate_fitid_by_amount:
                    fitid_match = re.search(r"<FITID>(.*?)</FITID>", block)
                    amt_match = re.search(r"<TRNAMT>(.*?)</TRNAMT>", block)
                    date_match = re.search(r"<DTPOSTED>(.*?)</DTPOSTED>", block)

                    if fitid_match and amt_match and date_match:
                        old_id = fitid_match.group(1).strip()
                        raw_amt = amt_match.group(1).strip()
                        raw_date = date_match.group(1).strip()[:8]

                        sign = "N" if "-" in raw_amt else "P"
                        digits = re.sub(r"[^0-9]", "", raw_amt)

                        # New ID joining old ID + date + amount
                        new_id = f"{old_id}-{raw_date}-{sign}{digits}"

                        block = block.replace(
                            f"<FITID>{fitid_match.group(1)}</FITID>",
                            f"<FITID>{new_id}</FITID>",
                        )
                return block

            pattern = r"(<STMTTRN>.*?</STMTTRN>)"
            content = re.sub(
                pattern, _process_block, content, flags=re.DOTALL | re.IGNORECASE
            )
            data_file = content.encode("utf-8")

        return super()._parse_file(data_file)
