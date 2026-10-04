import json
import unittest

from diagnostics_cli.cli import collect_diagnostics


class TestDiagnostics(unittest.TestCase):

    def test_python_information_exists(self):
        report = collect_diagnostics()
        self.assertIn("python", report)
        self.assertIn("version", report["python"])

    def test_disk_information_exists(self):
        report = collect_diagnostics()
        self.assertIn("disk", report)
        self.assertGreaterEqual(report["disk"]["total_gb"], 0)

    def test_developer_tools_exist(self):
        report = collect_diagnostics()
        self.assertIn("developer_tools", report)
        self.assertIn("python", report["developer_tools"])

    def test_report_is_json_serializable(self):
        report = collect_diagnostics()
        encoded = json.dumps(report)
        decoded = json.loads(encoded)
        self.assertEqual(decoded["status"], report["status"])


if __name__ == "__main__":
    unittest.main()
