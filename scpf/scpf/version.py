"""Guard against untested SolidCraft native command interpretations.

SCPF currently targets SolidCraft 0.30.1. In particular occurrence.move
absolute 'to' is not understood by v0.30.1, even though unknown fields were
accepted by older lax implementations. Always inspect the effective native
occurrence transform, not just command acceptance.
"""
import re
import shutil
import subprocess
import warnings

TESTED_SOLIDCRAFT_VERSION = "0.30.1"
_VERSION = re.compile(r"(?<!\d)(\d+)\.(\d+)\.(\d+)(?!\d)")


def parse_version(raw):
    match = _VERSION.search(str(raw))
    if match is None:
        raise ValueError(f"Unrecognized SolidCraft version string: {raw!r}")
    return tuple(int(part) for part in match.groups())


def validate_version(raw, tested=TESTED_SOLIDCRAFT_VERSION):
    """Return detected version; error on older, warn on newer/untested."""
    actual = parse_version(raw)
    expected = parse_version(tested)
    if actual < expected:
        raise RuntimeError(
            f"SolidCraft {'.'.join(map(str, actual))} is too old; "
            f"this SCPF build requires at least {tested}. "
            "Update SolidCraft before executing a native command plan."
        )
    if actual != expected:
        warnings.warn(
            f"SolidCraft {'.'.join(map(str, actual))} differs from tested "
            f"version {tested}; native command behavior must be verified.",
            RuntimeWarning,
            stacklevel=2,
        )
    return actual


def check_cli_version(executable="solidcraft-cli", require_cli=False):
    """Check local CLI version; does NOT prove a separate GUI's version.

    If CLI is absent, GUI live mode still works but is not version-verified.
    Headless/native CI should pass require_cli=True to fail if unavailable.
    """
    path = shutil.which(executable)
    if not path:
        if require_cli:
            raise RuntimeError(f"{executable} not found; SolidCraft version cannot be checked")
        warnings.warn(
            f"{executable} not found: cannot verify the running SolidCraft "
            f"GUI version. Expected {TESTED_SOLIDCRAFT_VERSION}.",
            RuntimeWarning,
            stacklevel=2,
        )
        return None
    try:
        result = subprocess.run(
            [path, "--version"], capture_output=True, text=True, check=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"Cannot obtain {executable} version: {exc}") from exc
    return validate_version((result.stdout or "") + " " + (result.stderr or ""))
