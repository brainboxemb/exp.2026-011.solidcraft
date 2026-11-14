"""Qualification: an imported @assembly compiles as a native subassembly."""

from subassembly import PostPair


class ImportedAssembly:
    def build(self):
        return PostPair()


ImportedAssembly()
