"""SolidCraft version compatibility guards should not silently accept older engines."""
import unittest
import warnings
from unittest.mock import patch
from scpf.version import (parse_version, validate_version, check_cli_version,
                          TESTED_SOLIDCRAFT_VERSION)


class NativeVersionTests(unittest.TestCase):
    def test_parse_cli_banner(self):
        self.assertEqual(parse_version("solidcraft-cli 0.30.1"), (0, 30, 1))
        self.assertEqual(parse_version("SolidCraft v0.31.0\n"), (0, 31, 0))
        with self.assertRaises(ValueError):
            parse_version("unrecognized banner")

    def test_tested_version_is_supported(self):
        with warnings.catch_warnings(record=True) as notes:
            warnings.simplefilter("always")
            self.assertEqual(validate_version("SolidCraft 0.30.1"), (0, 30, 1))
            self.assertEqual(notes, [])

    def test_older_engine_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "too old"):
            validate_version("solidcraft-cli 0.30.0")

    def test_newer_engine_warns(self):
        with self.assertWarnsRegex(RuntimeWarning, "differs from tested"):
            self.assertEqual(validate_version("SolidCraft 0.31.0"), (0, 31, 0))

    def test_no_cli_warns_in_gui_mode(self):
        with patch("scpf.version.shutil.which", return_value=None):
            with self.assertWarnsRegex(RuntimeWarning, "cannot verify"):
                self.assertIsNone(check_cli_version())
            with self.assertRaisesRegex(RuntimeError, "not found"):
                check_cli_version(require_cli=True)

    def test_detect_cli_version_from_subprocess(self):
        with patch("scpf.version.shutil.which", return_value="/fake/solidcraft-cli"):
            with patch("scpf.version.subprocess.run") as run:
                run.return_value.stdout = "solidcraft-cli 0.30.1\n"
                run.return_value.stderr = ""
                self.assertEqual(check_cli_version(require_cli=True), (0, 30, 1))
                run.assert_called_once()
