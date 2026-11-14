"""Qualification: group(name) becomes a real nested native component."""


class Panel:
    def build(self):
        return Box(10, 2, 20)


class Frame:
    def build(self):
        return Box(35, 10, 40)


class GroupHierarchy:
    def build(self):
        left = Panel()
        panels = (left + left.copy().move(x=11)).group("PanelGroup")
        frame = Frame().move(y=20)
        return panels + frame


GroupHierarchy()
