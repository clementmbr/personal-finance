# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import logging
import math
from datetime import datetime

from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    import xlrd
    from xlrd.xldate import xldate_as_datetime
except (OSError, ImportError) as err:  # pragma: no cover
    _logger.error(err)


class AccountStatementImportSheetParser(models.TransientModel):
    _inherit = "account.statement.import.sheet.parser"

    def _get_column_names(self):
        res = super()._get_column_names()
        res.extend(["category_column", "subcategory_column", "analytic_account_column"])
        return res

    def _parse_rows(self, mapping, currency_code, data, columns):  # noqa: C901
        # Rewrite everything because the guys didn't use a inheritable method in the
        # for loop :'( :'(
        # ------------------------------------------------------

        csv_or_xlsx, data_file = data

        # Get the numbers of rows of the file
        if isinstance(csv_or_xlsx, tuple):
            numrows = csv_or_xlsx[1].nrows
        else:
            numrows = len(str(data_file.strip()).split("\\n"))

        label_line = mapping.header_lines_skip_count
        footer_line = numrows - mapping.footer_lines_skip_count

        if isinstance(csv_or_xlsx, tuple):
            rows = range(label_line, footer_line)
        else:
            rows = csv_or_xlsx

        lines = []
        for index, row in enumerate(rows, label_line):
            if isinstance(csv_or_xlsx, tuple):
                book = csv_or_xlsx[0]
                sheet = csv_or_xlsx[1]
                values = []
                for col_index in range(mapping.offset_column, sheet.row_len(row)):
                    cell_type = sheet.cell_type(row, col_index)
                    cell_value = sheet.cell_value(row, col_index)
                    if cell_type == xlrd.XL_CELL_DATE:
                        cell_value = xldate_as_datetime(cell_value, book.datemode)
                    values.append(cell_value)
            else:
                if index >= footer_line:
                    continue
                values = list(row)
            if mapping.skip_empty_lines and not any(values):
                continue

            timestamp = self._get_values_from_column(
                values, columns, "timestamp_column"
            )
            currency = (
                self._get_values_from_column(values, columns, "currency_column")
                if columns["currency_column"]
                else currency_code
            )

            def _decimal(column_name, values):
                if columns[column_name]:
                    return self._parse_decimal(
                        self._get_values_from_column(values, columns, column_name),
                        mapping,
                    )

            amount = _decimal("amount_column", values)
            if not amount:
                amount = abs(_decimal("amount_debit_column", values) or 0)
            if not amount:
                amount = -abs(_decimal("amount_credit_column", values) or 0)

            balance = (
                self._get_values_from_column(values, columns, "balance_column")
                if columns["balance_column"]
                else None
            )
            original_currency = (
                self._get_values_from_column(
                    values, columns, "original_currency_column"
                )
                if columns["original_currency_column"]
                else None
            )
            original_amount = (
                self._get_values_from_column(values, columns, "original_amount_column")
                if columns["original_amount_column"]
                else None
            )
            debit_credit = (
                self._get_values_from_column(values, columns, "debit_credit_column")
                if columns["debit_credit_column"]
                else None
            )
            transaction_id = (
                self._get_values_from_column(values, columns, "transaction_id_column")
                if columns["transaction_id_column"]
                else None
            )
            description = (
                self._get_values_from_column(values, columns, "description_column")
                if columns["description_column"]
                else None
            )
            notes = (
                self._get_values_from_column(values, columns, "notes_column")
                if columns["notes_column"]
                else None
            )
            reference = (
                self._get_values_from_column(values, columns, "reference_column")
                if columns["reference_column"]
                else None
            )
            partner_name = (
                self._get_values_from_column(values, columns, "partner_name_column")
                if columns["partner_name_column"]
                else None
            )
            bank_name = (
                self._get_values_from_column(values, columns, "bank_name_column")
                if columns["bank_name_column"]
                else None
            )
            bank_account = (
                self._get_values_from_column(values, columns, "bank_account_column")
                if columns["bank_account_column"]
                else None
            )

            debit_column = (
                self._get_values_from_column(values, columns, "amount_debit_column")
                if columns["amount_debit_column"]
                else None
            )

            credit_column = (
                self._get_values_from_column(values, columns, "amount_credit_column")
                if columns["amount_credit_column"]
                else None
            )

            if currency != currency_code:
                continue

            if isinstance(timestamp, str):
                timestamp = datetime.strptime(timestamp, mapping.timestamp_format)
                if timestamp.year == 1900:
                    # No year indicated, so put the current or previous one depending
                    # on the current month (i.e. in January, importing December)
                    now = datetime.now()
                    year = now.year
                    if timestamp.month > now.month:
                        year -= 1
                    timestamp = timestamp.replace(year=year)

            if balance:
                balance = self._parse_decimal(balance, mapping)
            else:
                balance = None

            if debit_credit is not None:
                amount = abs(amount)
                if debit_credit == mapping.debit_value:
                    amount = -amount

            if debit_column and credit_column:
                debit_amount = self._parse_decimal(debit_column, mapping)
                debit_amount = abs(debit_amount)
                credit_amount = self._parse_decimal(credit_column, mapping)
                credit_amount = abs(credit_amount)
                amount = -(credit_amount - debit_amount)

            if original_amount:
                original_amount = math.copysign(
                    self._parse_decimal(original_amount, mapping), amount
                )
            else:
                original_amount = 0.0
            if mapping.amount_inverse_sign:
                amount = -amount
                original_amount = -original_amount
                balance = -balance if balance is not None else balance
            line = {
                "timestamp": timestamp,
                "amount": amount,
                "currency": currency,
                "original_amount": original_amount,
                "original_currency": original_currency,
            }
            if balance is not None:
                line["balance"] = balance
            if transaction_id is not None:
                line["transaction_id"] = transaction_id
            if description is not None:
                line["description"] = description
            if notes is not None:
                line["notes"] = notes
            if reference is not None:
                line["reference"] = reference
            if partner_name is not None:
                line["partner_name"] = partner_name
            if bank_name is not None:
                line["bank_name"] = bank_name
            if bank_account is not None:
                line["bank_account"] = bank_account

            # --- START NEW CODE ----

            category_name = (
                self._get_values_from_column(values, columns, "category_column")
                if columns["category_column"]
                else None
            )
            subcategory_name = (
                self._get_values_from_column(values, columns, "subcategory_column")
                if columns["subcategory_column"]
                else None
            )
            analytic_account_name = (
                self._get_values_from_column(values, columns, "analytic_account_column")
                if columns["analytic_account_column"]
                else None
            )

            if category_name is not None:
                line["category_name"] = category_name
            if subcategory_name is not None:
                line["subcategory_name"] = subcategory_name
            if analytic_account_name is not None:
                line["analytic_account_name"] = analytic_account_name

            # ----  END NEW CODE ----

            if line:
                lines.append(line)
        return lines

    @api.model
    def _convert_line_to_transactions(self, line):  # noqa: C901
        [transaction] = super()._convert_line_to_transactions(line)

        category_name = line.get("category_name")
        if category_name:
            category = self.env["bank.statement.line.category"].search(
                [("name", "=", category_name), ("parent_id", "=", False)], limit=1
            )
            transaction["category_id"] = category.id

        subcategory_name = line.get("subcategory_name")
        if subcategory_name:
            subcategory = self.env["bank.statement.line.category"].search(
                [("name", "=", subcategory_name), ("parent_id", "!=", False)], limit=1
            )
            transaction["subcategory_id"] = subcategory.id

        analytic_account_name = line.get("analytic_account_name")
        if analytic_account_name:
            analytic_account = self.env["account.analytic.account"].search(
                [("name", "=", analytic_account_name)], limit=1
            )
            transaction["analytic_account_id"] = analytic_account.id

        return [transaction]
