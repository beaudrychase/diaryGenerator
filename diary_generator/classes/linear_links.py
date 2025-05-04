from typing import Literal

import fitz

from diary_generator.classes.links import Links
from diary_generator.classes.page import Page


class LinearLinks(Links):
    # Renders a set of links left to right, or top to bottom,
    # as a set of boxes, containing centered label text.
    #
    # Expects one of left / right to be passed in constructor
    # Expects one of top/bottom to be passed in constructor
    #
    # Starting from the point defined by the two elements above,
    # boxes will be laid out either from the left (if "left" is passed)
    # or from the right (if "right" is passed).
    #
    # If right is passed, it can either be expressed as an positive number,
    # in which case it is considered as an absolute x coordinate, or as
    # a negative number, in which case it is considered as an offset from
    # the right edge of the document.
    #
    # Similarly if bottom is passed and is positive, it is considered as
    # an absolute y cooridinate, but if negative it is considered as
    # an offset from the page bottom.
    #
    # The size of each box can be modified by the width and height args-
    # Note that is the label text is too large it will just not rendered
    #
    # Use flowdirection="right" to choose left to right,
    # and flowdirection="down" to choose top to bottom
    # The fontsize is also controllable.

    horizontal_anchor: Literal["left", "right"]
    horizontal_anchor_offset: int
    vertical_achor: Literal["top", "bottom"]
    vertical_achor_offset: int
    width: int
    height: int
    flow_direction: Literal["right", "down"]
    font_size: int

    pages: list[Page]
    labels: dict[Page, str]

    def __init__(
        self,
        horizontal_anchor: Literal["left", "right"],
        horizontal_anchor_offset: int,
        vertical_achor: Literal["top", "bottom"],
        vertical_achor_offset: int,
        width=80,
        height=80,
        flow_direction: Literal["right", "down"] = "right",
        font_size=30,
    ):

        self.horizontal_anchor = horizontal_anchor
        self.horizontal_anchor_offset = horizontal_anchor_offset
        self.vertical_achor = vertical_achor
        self.vertical_achor_offset = vertical_achor_offset

        self.flow_direction = flow_direction

        self.width = width
        self.height = height
        self.font_size = font_size

        self.labels = dict()
        self.pages = list()

    def add_link(self, page: Page, label: str):
        self.labels[page] = label
        self.pages.append(page)

    # Render this set of link boxes onto the passed page
    # This method will automatically display a box as inverse color
    # if the link points back to itself.
    def render(self, page: fitz.Page, page_number: int):
        if self.flow_direction == "right":
            if self.horizontal_anchor == "left":
                l = self.horizontal_anchor_offset
            else:
                l = (
                    page.rect.x1
                    + self.horizontal_anchor_offset
                    - len(self.pages) * self.width
                )

            r = l + self.width

            if self.vertical_achor == "top":
                t = self.vertical_achor_offset
            else:
                t = page.rect.y1 + self.vertical_achor_offset - self.height

            b = t + self.height
        else:  # flow down from top
            if self.horizontal_anchor == "left":
                l = self.horizontal_anchor_offset
            else:
                l = page.rect.x1 + self.horizontal_anchor_offset - self.width

            r = l + self.width

            if self.vertical_achor == "top":
                t = self.vertical_achor_offset
            else:
                t = (
                    page.rect.y1
                    + self.horizontal_anchor_offset
                    - self.height * len(self.pages)
                )

            b = t + self.height

        boxcol = fitz.utils.getColor("black")

        for target in self.pages:

            if target.page_number == page_number:
                textcol = fitz.utils.getColor("white")
                backcol = fitz.utils.getColor("black")
            else:
                textcol = fitz.utils.getColor("black")
                backcol = fitz.utils.getColor("white")
            r1 = fitz.Rect(l, t, r, b)
            textrect = fitz.Rect(
                l, t + (self.height / 2) - (self.font_size / 2 * 1.33), r, b
            )
            page.draw_rect(r1, color=boxcol, fill=backcol, overlay=True)  # type: ignore

            if self.flow_direction == "right":
                r = r + self.width
                l = l + self.width
            else:
                t = t + self.height
                b = b + self.height

            linkdict = {"kind": 1, "from": r1, "page": target.page_number}
            page.insert_link(linkdict)  # type: ignore

            # this line should use link text
            page.insert_textbox(  # type: ignore
                textrect,
                f"{self.labels[target]}",
                color=textcol,
                overlay=True,
                align=1,
                fontsize=self.font_size,
            )
