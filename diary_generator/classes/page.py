import fitz

from diary_generator.classes.links import Links


class Page:
    title: str
    title_x: int
    title_y: int
    title_size: int
    toc_level: int
    link_sets: list[Links]
    base_pdf: fitz.Document

    def __init__(
        self,
        base_pdf: fitz.Document,
        title="",
        title_x=20,
        title_y=250,
        title_size=50,
        toc_level=0,
    ):
        self.base_pdf = base_pdf
        self.title = title
        self.link_sets = []
        self.page_number = 0
        self.title_col = fitz.utils.getColor("black")
        self.title_size = title_size
        self.title_x = title_x
        self.title_y = title_y
        self.toc_level = toc_level

    def add_links(self, *linksets: Links):
        for linkset in linksets:
            self.link_sets.append(linkset)
        return self

    def render(self, fitzdoc: fitz.Document):
        fitzpage = fitzdoc[self.page_number]
        # render outbound links
        for linkset in self.link_sets:
            linkset.render(fitzpage, self.page_number)
        # render title
        fitzpage.insert_text(  # type: ignore
            (self.title_x, self.title_y),
            self.title,
            color=self.title_col,
            overlay=True,
            fontsize=self.title_size,
        )
