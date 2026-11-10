# SCPF repository notes

Python SCPF is the only supported scripting frontend. Keep model objects
and CAD feature intent separate from SolidCraft command JSON and transport.
The adapter may translate one high-level feature into multiple native commands.
SolidCraft remains the only engine for BRep geometry and native feature history.

When changing example models, update Python regression tests, generated command
fixtures where applicable, and native qualification checks. Do not reintroduce
the retired SCRF Rust scripting layer.
