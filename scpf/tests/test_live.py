"""Protocol tests with a local fake SolidCraft control channel.

No real GUI or SolidCraft installation is needed in CI. The server checks
the exact wire request; native GUI execution remains a separate test.
"""
import json
import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest
from unittest.mock import patch

from scpf.live import LiveError, new_design, send_commands
from scpf.__main__ import read_command_file, main
from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]


class FakeSolidCraft:
    def __init__(self, reply):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(("127.0.0.1", 0))
        replies = reply if isinstance(reply, list) else [reply]
        self.listener.listen(len(replies))
        self.port = self.listener.getsockname()[1]
        self.replies = replies
        self.requests = []
        self.request = None
        self.thread = threading.Thread(target=self.serve, daemon=True)
        self.thread.start()

    def serve(self):
        try:
            with self.listener:
                for reply in self.replies:
                    conn, _ = self.listener.accept()
                    with conn:
                        with conn.makefile("rb") as stream:
                            self.request = json.loads(stream.readline())
                            self.requests.append(self.request)
                        conn.sendall((json.dumps(reply) + "\n").encode("utf-8"))
        except OSError:
            pass

    def join(self):
        self.thread.join(timeout=3)
        if self.thread.is_alive():
            self.listener.close()
            raise AssertionError("fake server did not receive a request")


class LiveProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def configure(self, server):
        (self.directory / "current.port").write_text(str(server.port))
        (self.directory / f"{server.port}.token").write_text("abcdeffedcba")

    def test_live_plate_is_single_strict_atomic_batch(self):
        document = run_script(ROOT / "examples/plate/scpf/model.py")
        commands = document["commands"]
        server = FakeSolidCraft({
            "id": 1, "ok": True,
            "result": {"completed": len(commands), "results": [{} for _ in commands],
                       "undone": 0},
        })
        self.configure(server)
        result = send_commands(commands, directory=self.directory)
        server.join()
        self.assertEqual(result["completed"], len(commands))
        self.assertEqual(server.request["method"], "engine.batch")
        self.assertEqual(server.request["token"], "abcdeffedcba")
        self.assertEqual(server.request["params"]["commands"], commands)
        self.assertEqual(server.request["params"]["rollback"], True)
        self.assertEqual(server.request["params"]["param_check"], "strict")

    def test_new_design_uses_native_file_new(self):
        server = FakeSolidCraft({
            "id": 1,
            "ok": True,
            "result": {"name": "Untitled"},
        })
        self.configure(server)
        result = new_design(directory=self.directory)
        server.join()
        self.assertEqual(result["name"], "Untitled")
        self.assertEqual(server.request["method"], "engine.execute")
        self.assertEqual(server.request["params"]["command"], "file.new")
        self.assertEqual(server.request["params"]["params"], {})
        self.assertEqual(server.request["params"]["param_check"], "strict")

    def test_cli_new_creates_empty_design_before_model_batch(self):
        document = run_script(ROOT / "examples/plate/scpf/model.py")
        commands = document["commands"]
        server = FakeSolidCraft([
            {
                "id": 1,
                "ok": True,
                "result": {"name": "Untitled"},
            },
            {
                "id": 1,
                "ok": True,
                "result": {
                    "completed": len(commands),
                    "results": [{} for _ in commands],
                    "undone": 0,
                },
            },
        ])
        self.configure(server)
        with patch.dict(os.environ, {"SOLIDCRAFT_CONTROL_DIR": str(self.directory)}):
            self.assertEqual(
                main([
                    str(ROOT / "examples/plate/scpf/model.py"),
                    "--connect",
                    "--new",
                ]),
                0,
            )
        server.join()
        self.assertEqual(
            [request["method"] for request in server.requests],
            ["engine.execute", "engine.batch"],
        )
        self.assertEqual(
            server.requests[0]["params"]["command"],
            "file.new",
        )
        self.assertEqual(
            server.requests[1]["params"]["commands"],
            commands,
        )

    def test_live_bracket_can_send_native_commands(self):
        commands = run_script(ROOT / "examples/bracket/scpf/model.py")["commands"]
        server = FakeSolidCraft({
            "id": 1, "ok": True, "result": {"completed": len(commands), "results": [],
                                              "undone": 0},
        })
        self.configure(server)
        send_commands(commands, connect=f"127.0.0.1:{server.port}", directory=self.directory)
        server.join()
        self.assertEqual(server.request["params"]["commands"][0]["command"], "parameters.add")

    def test_replay_existing_json_unchanged_to_live_gui(self):
        commands_file = ROOT / "examples/bracket/source/bracket.json"
        original = json.loads(commands_file.read_text(encoding="utf-8"))
        self.assertEqual(read_command_file(commands_file), original)
        server = FakeSolidCraft({
            "id": 1, "ok": True,
            "result": {"completed": len(original["commands"]), "results": []},
        })
        self.configure(server)
        with patch.dict(os.environ, {"SOLIDCRAFT_CONTROL_DIR": str(self.directory)}):
            self.assertEqual(main(["replay", str(commands_file)]), 0)
        server.join()
        self.assertEqual(server.request["params"]["commands"], original["commands"])
        self.assertEqual(server.request["params"]["commands"][0]["command"],
                         "parameters.change")

    def test_replay_rejects_invalid_command_document(self):
        invalid = self.directory / "invalid.json"
        invalid.write_text('{"not_commands":[]}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "commands"):
            read_command_file(invalid)

    def test_replay_rejects_out_option(self):
        with self.assertRaises(SystemExit) as error:
            main(["replay", str(ROOT / "examples/bracket/source/bracket.json"),
                  "--out", "copied.json"])
        self.assertEqual(error.exception.code, 2)

    def test_new_requires_connect(self):
        with self.assertRaises(SystemExit) as error:
            main([
                str(ROOT / "examples/plate/scpf/model.py"),
                "--out",
                str(self.directory / "plate.json"),
                "--new",
            ])
        self.assertEqual(error.exception.code, 2)

    def test_live_rollback_failure_is_reported(self):
        commands = [{"command": "solid.box", "params": {}}]
        server = FakeSolidCraft({
            "id": 1, "ok": True,
            "result": {"completed": 0, "undone": 0, "rolled_back": True,
                       "failed": {"index": 0, "command": "solid.box", "error": "invalid size"}},
        })
        self.configure(server)
        with self.assertRaisesRegex(LiveError, "Rolled back: True"):
            send_commands(commands, directory=self.directory)
        server.join()

    def test_auth_failure_does_not_claim_success(self):
        commands = [{"command": "solid.box", "params": {}}]
        server = FakeSolidCraft({"id": 1, "ok": False, "error": "unauthorized"})
        self.configure(server)
        with self.assertRaisesRegex(LiveError, "unauthorized"):
            send_commands(commands, directory=self.directory)
        server.join()

    def test_missing_gui_is_an_error_not_a_new_headless_session(self):
        with self.assertRaisesRegex(LiveError, "No live SolidCraft port"):
            send_commands([{"command": "solid.box", "params": {}}],
                          directory=self.directory)

    def test_nonlocal_destination_is_rejected(self):
        with self.assertRaisesRegex(LiveError, "127.0.0.1"):
            send_commands([{"command": "solid.box", "params": {}}],
                          connect="example.com:1234", directory=self.directory)

    def test_invalid_response_does_not_claim_success(self):
        server = FakeSolidCraft({"id": 1, "ok": True, "result": {"completed": 0}})
        self.configure(server)
        with self.assertRaisesRegex(LiveError, "only 0"):
            send_commands([{"command": "solid.box", "params": {}}],
                          directory=self.directory)
        server.join()


if __name__ == "__main__":
    unittest.main()
