# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import logging
import re

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AccountStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    clean_ofx_file = fields.Boolean(
        string="Clean OFX file",
        help="Remove invalid transactions with empty FITID"
        "(e.g., daily balance lines from some banks).",
    )

    def _parse_file(self, data_file):
        if self.clean_ofx_file and data_file:
            _logger.info("Cleaning OFX file: removing blocks with empty FITID.")
            try:
                content = data_file.decode("utf-8")
            except UnicodeDecodeError:
                content = data_file.decode("latin-1")

            def _clean_block(match):
                """Return empty string if FITID is empty, else return block."""
                block = match.group(0)
                # Check for <FITID></FITID> or <FITID>  </FITID>
                if re.search(r"<FITID>\s*</FITID>", block, flags=re.DOTALL):
                    return ""
                return block

            # Capture each STMTTRN block non-greedily
            pattern = r"(<STMTTRN>.*?</STMTTRN>)"
            content = re.sub(
                pattern, _clean_block, content, flags=re.DOTALL | re.IGNORECASE
            )

            data_file = content.encode("utf-8")

        return super()._parse_file(data_file)
