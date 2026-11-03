"""离线检查案例选择和只读CLI，确保未选中或预览时不会发出真实评测。"""

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from learning.evaluation import step_02_run_first_case as runner


class CaseSelectionTests(unittest.TestCase):
    def setUp(self):
        self.cases = [{"id": "first"}, {"id": "second"}]

    def test_default_retains_first_case(self):
        self.assertIs(runner.select_case(self.cases), self.cases[0])

    def test_selects_second_case_by_id(self):
        self.assertIs(runner.select_case(self.cases, "second"), self.cases[1])

    def test_unknown_id_rejected(self):
        with self.assertRaisesRegex(ValueError, "找不到案例ID"):
            runner.select_case(self.cases, "not-present")

    def test_duplicate_id_rejected(self):
        with self.assertRaisesRegex(ValueError, "案例ID重复"):
            runner.select_case([{"id": "same"}, {"id": "same"}], "same")

    def test_readonly_modes_and_invalid_selection_do_not_run_eval(self):
        with patch.object(runner, "collect_case") as collect:
            for argv in (["--list-cases"], ["--show-case"]):
                with self.subTest(argv=argv), redirect_stdout(io.StringIO()) as output:
                    runner.main(argv)
                    self.assertIn("order_tracking_10001", output.getvalue())
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stopped:
                runner.main(["--case-id", "definitely-not-present"])
            self.assertEqual(stopped.exception.code, 2)
            collect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
