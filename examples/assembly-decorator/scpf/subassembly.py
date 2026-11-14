"""Reusable subassembly used by the @assembly qualification fixture."""

from scpf.core import Box
from scpf.runner import assembly, component


@component
class Post:
    def build(self):
        return Box(10, 10, 20)


@assembly
class PostPair:
    def build(self):
        left = Post(name="left").move(x=-15)
        right = left.copy().move(x=30)
        return left + right
