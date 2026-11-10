"""Send compiled CAD commands to an already running SolidCraft desktop app.

This is a small client for SolidCraft's *existing* authenticated control
protocol, not an MCP server. It never starts a headless CAD session.

Protocol: https://docs.solidcraft.io/dev/control-protocol.html
"""
import json
import os
from pathlib import Path
import socket
import sys


class LiveError(RuntimeError):
    """Live SolidCraft connection or command execution failed."""


def control_directory():
    override = os.environ.get("SOLIDCRAFT_CONTROL_DIR")
    if override:
        return Path(override).expanduser()
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA")
        if not base:
            raise LiveError("LOCALAPPDATA is not set. Pass a control directory.")
        return Path(base) / "SolidCraft" / "control"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "SolidCraft" / "control"
    return Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "solidcraft" / "control"


def locate_port(directory):
    path = directory / "current.port"
    try:
        value = path.read_text(encoding="ascii").strip()
        port = int(value)
    except (OSError, ValueError) as exc:
        raise LiveError(
            f"No live SolidCraft port in {path}. Start the SolidCraft GUI "
            "and enable Preferences > Assistant > Let AI agents connect."
        ) from exc
    if not 1 <= port <= 65535:
        raise LiveError(f"Invalid SolidCraft control port in {path}: {port}")
    return port


def parse_connect(connect, directory):
    if connect is True or connect == "auto":
        return locate_port(directory)
    if isinstance(connect, int):
        port = connect
    elif isinstance(connect, str):
        address = connect.removeprefix("127.0.0.1:")
        try:
            port = int(address)
        except ValueError as exc:
            raise LiveError("Use --connect or --connect 127.0.0.1:PORT") from exc
    else:
        raise LiveError("Invalid --connect value")
    if not 1 <= port <= 65535:
        raise LiveError("Control port must be 1..65535")
    return port


def read_launch_token(directory, port):
    env_token = os.environ.get("SOLIDCRAFT_CONTROL_TOKEN")
    if env_token:
        return env_token
    path = directory / f"{port}.token"
    try:
        token = path.read_text(encoding="ascii").strip()
    except OSError as exc:
        raise LiveError(
            f"No SolidCraft authentication token at {path}. "
            "The GUI may not be running, or the token path differs."
        ) from exc
    if not token:
        raise LiveError(f"Empty SolidCraft token: {path}")
    return token


def _read_reply(connection):
    # The control protocol has one JSON object per newline. A batch can
    # take some time in the GUI; a timeout is NOT proof that nothing happened.
    with connection.makefile("rb") as stream:
        line = stream.readline(16 * 1024 * 1024 + 1)
    if not line:
        raise LiveError("SolidCraft closed the control connection without a reply")
    if len(line) > 16 * 1024 * 1024:
        raise LiveError("SolidCraft response exceeded 16 MiB")
    try:
        answer = json.loads(line)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LiveError("Invalid response from SolidCraft control channel") from exc
    if answer.get("id") != 1 or "ok" not in answer:
        raise LiveError("Unexpected control-channel response")
    return answer


def send_commands(commands, *, connect="auto", directory=None, timeout=3610):
    """Execute native command plan *in the open GUI* as one rollback batch.

    On command failure the server normally rolls back all changes. No new
    tab, GUI launch or file save is performed. The active design is modified
    on success; the user should start with a new blank design.
    """
    if not isinstance(commands, list) or not commands:
        raise LiveError("No commands to send")
    if len(commands) > 10000:
        raise LiveError("SolidCraft engine.batch supports at most 10,000 commands")
    for index, entry in enumerate(commands):
        if not isinstance(entry, dict) or not isinstance(entry.get("command"), str):
            raise LiveError(f"Invalid command at index {index}")
        if not isinstance(entry.get("params", {}), dict):
            raise LiveError(f"Invalid command parameters at index {index}")
    directory = Path(directory) if directory is not None else control_directory()
    port = parse_connect(connect, directory)
    token = read_launch_token(directory, port)
    request = {
        "id": 1,
        "method": "engine.batch",
        "token": token,
        "params": {
            "commands": commands,
            "rollback": True,
            "param_check": "strict",
        },
    }
    encoded = (json.dumps(request, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    if len(encoded) > 16 * 1024 * 1024:
        raise LiveError("Batch request exceeds SolidCraft control protocol limit")
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=5) as connection:
            connection.settimeout(timeout)
            connection.sendall(encoded)
            answer = _read_reply(connection)
    except (ConnectionRefusedError, ConnectionResetError, OSError) as exc:
        if isinstance(exc, socket.timeout):
            raise LiveError(
                "Control channel timed out. The batch MAY STILL BE RUNNING in "
                "SolidCraft. Inspect the app; do not send it again blindly."
            ) from exc
        raise LiveError(
            f"Cannot talk to the running SolidCraft GUI at 127.0.0.1:{port}: {exc}"
        ) from exc

    if not answer["ok"]:
        raise LiveError(f"SolidCraft rejected the batch: {answer.get('error', answer)}")
    result = answer.get("result")
    if not isinstance(result, dict):
        raise LiveError(f"Unexpected batch result: {result!r}")
    if result.get("failed") is not None:
        failed = result["failed"]
        rolled_back = result.get("rolled_back", False)
        raise LiveError(
            f"SolidCraft command failed at step {failed.get('index')}: "
            f"{failed.get('command')}: {failed.get('error')}. "
            f"Rolled back: {rolled_back}"
        )
    if result.get("completed") != len(commands):
        raise LiveError(f"SolidCraft reported only {result.get('completed')} of {len(commands)} completed commands")
    return result
