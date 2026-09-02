# Copyright 2026 Akretion France (http://www.akretion.com/)
import logging
import re

from odoo import models

_logger = logging.getLogger(__name__)


class AccountStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    # N-B: The OfxParser reject files with empty FITID, so we need to modify the file
    # in _parse_file() and rewrite the code to find the journal even if the original
    # module account_statement_import_file does it later in _complete_stmts_vals()

    def _parse_file(self, data_file):
        """
        Optimized pre-processing: decode once, find journal, and clean if needed.
        """

        if not self.statement_filename.lower().endswith(".ofx"):
            return super()._parse_file(data_file)

        content = data_file.decode("utf-8", errors="ignore")
        journal = self._find_journal_for_clean(content)

        # Clean string content if necessary
        if journal and (
            journal.ignore_empty_fitid or journal.deduplicate_fitid_by_amount
        ):
            content = self._clean_ofx_content(content, journal)
            data_file = content.encode("utf-8")

        return super()._parse_file(data_file)

    def _find_journal_for_clean(self, content):
        """
        Extract identification tags and use Odoo's native matching.
        """
        acc_match = re.search(r"<ACCTID>([^<\r\n]+)", content, re.I)
        cur_match = re.search(r"<CURDEF>([^<\r\n]+)", content, re.I)

        account_number = acc_match.group(1).strip() if acc_match else None
        currency_code = cur_match.group(1).strip() if cur_match else None
        currency = self._match_currency(currency_code)

        return self._match_journal(account_number, currency)

    def _clean_ofx_content(self, content, journal):
        """
        Process blocks using re.sub with a callback function.
        """

        def _process_block(match):
            block = match.group(0)

            # Logic: Remove Empty FITID
            if journal.ignore_empty_fitid:
                if re.search(r"<FITID>\s*</FITID>", block, re.I):
                    return ""

            # Logic: Deduplicate FITID by Amount
            if journal.deduplicate_fitid_by_amount:
                fitid_match = re.search(r"<FITID>(.*?)</FITID>", block, re.I)
                amount_match = re.search(r"<TRNAMT>(.*?)</TRNAMT>", block, re.I)
                date_match = re.search(r"<DTPOSTED>(.*?)</DTPOSTED>", block, re.I)

                if fitid_match and amount_match and date_match:
                    old_id = fitid_match.group(1).strip()
                    raw_amt = amount_match.group(1).strip()
                    raw_date = date_match.group(1).strip()[:8]

                    sign = "N" if "-" in raw_amt else "P"
                    digits = re.sub(r"\D", "", raw_amt)  # \D = any non-digit

                    new_id = f"{old_id}-{raw_date}-{sign}{digits}"
                    block = block.replace(
                        fitid_match.group(0), f"<FITID>{new_id}</FITID>"
                    )

            return block

        return re.sub(
            r"<STMTTRN>.*?</STMTTRN>", _process_block, content, flags=re.DOTALL | re.I
        )
