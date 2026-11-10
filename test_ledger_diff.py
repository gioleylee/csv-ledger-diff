from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from ledger_diff import compare


class LedgerDiffTests(TestCase):
    def test_compares_reordered_snapshots(self):
        with TemporaryDirectory() as directory:
            before, after = (Path(directory) / name for name in ("old.csv", "new.csv"))
            before.write_text("id,amount\n001,5\n002,8\n004,1\n", encoding="utf-8-sig")
            after.write_text("amount,id\n1,004\n9,003\n6,001\n", encoding="utf-8")
            self.assertEqual(compare(before, after, "id"), {
                "added": [{"id": "003", "amount": "9"}],
                "removed": [{"id": "002", "amount": "8"}],
                "changed": {"001": {"amount": {"before": "5", "after": "6"}}},
            })

    def test_rejects_duplicate_key(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text("id,value\na,1\na,2\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate key"):
                compare(path, path, "id")
