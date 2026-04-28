from odoo.tests.common import TransactionCase


class TestAutoCategory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Setup category and sub-category
        cls.category = cls.env["bank.statement.line.category"].create({"name": "Food"})
        cls.subcategory_id = cls.env["bank.statement.line.category"].create(
            {"name": "Groceries", "parent_id": cls.category.id}
        )

        # Setup bank journal
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Bank Test",
                "code": "BNKT",
                "type": "bank",
            }
        )

        # Create a past categorized line
        cls.past_line = cls.env["account.bank.statement.line"].create(
            {
                "payment_ref": "SUPERMARKET A",
                "date": "2026-01-01",
                "amount": -50.0,
                "journal_id": cls.journal.id,
                "category_id": cls.category.id,
                "subcategory_id": cls.subcategory_id.id,
            }
        )

    def test_auto_category_assignment(self):
        """New line with exact same payment_ref should inherit categories"""
        new_line = self.env["account.bank.statement.line"].create(
            {
                "payment_ref": "SUPERMARKET A",
                "date": "2026-01-15",
                "amount": -20.0,
                "journal_id": self.journal.id,
            }
        )

        self.assertEqual(new_line.category_id, self.category)
        self.assertEqual(new_line.subcategory_id, self.subcategory_id)

    def test_no_auto_category_for_different_ref(self):
        """Unknown payment_ref should not get a category"""
        new_line = self.env["account.bank.statement.line"].create(
            {
                "payment_ref": "UNKNOWN SHOP",
                "date": "2026-01-16",
                "amount": -10.0,
                "journal_id": self.journal.id,
            }
        )

        self.assertFalse(new_line.category_id)
