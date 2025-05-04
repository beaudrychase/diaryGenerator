from typing import Optional

import fitz

from diary_generator.classes.page import Page
from diary_generator.classes.table_of_content_entry import TableOfContentEntry


class Doc:
    # Represents the output document
    # This class exists primarily to collect the invidual pages, in the correct order.
    # As the intra pdf linking scheme relies on page number, all pages must be known
    # before links are created.
    #
    # Requires the path to a tempate pdf file when created:
    # the first page of this file will be used as the default
    # template for each page created, if the page itself does
    # not have a dedicated template.
    pages: list[Page]
    fitz_doc: fitz.Document
    toc: list[TableOfContentEntry]

    def __init__(self, base_pdf_name: str):
        self.pages = []
        self.fitz_doc = fitz.open()
        self.base_pdf_name = base_pdf_name
        self.toc = []

    def add_page(
        self,
        base_pdf_name: Optional[str] = None,
        title="",
        title_x=20,
        title_y=250,
        title_size=50,
        toc_level=0,
    ):
        base_pdf = self._get_base_pdf_for_page(base_pdf_name)
        page = Page(
            base_pdf,
            title=title,
            title_x=title_x,
            title_y=title_y,
            title_size=title_size,
            toc_level=toc_level,
        )
        self.addPages(page)
        return page

    def _get_base_pdf_for_page(self, base_pdf_name: Optional[str]) -> fitz.Document:
        if base_pdf_name is None:
            return fitz.open(self.base_pdf_name)
        else:
            return fitz.open(base_pdf_name)

    # Add one or more pages into the document.
    # This method will create fitz pages for each doc, however rendering of content
    # is done as a separate pass
    def addPages(self, *pages: Page):
        for page in pages:
            self.pages.append(page)
            page.page_number = len(self.pages) - 1
            # copy tempate into new doc
            self.fitz_doc.insert_pdf(
                page.base_pdf,
                from_page=0,
                to_page=0,
                start_at=-1,
                rotate=-1,
                links=True,
                annots=True,
                show_progress=0,
                final=1,
            )
            if page.toc_level != 0:
                self.toc.append((page.toc_level, page.title, page.page_number))

    # Ask each page to render their own conent- this is done once all pages are added
    # After rendering the document is saved.
    def render(self, output_file_name: str):
        for page in self.pages:
            page.render(self.fitz_doc)
        self.fitz_doc.set_toc(self.toc, collapse=1)  # type: ignore
        self.fitz_doc.save(output_file_name)
