import math
from functools import partial
from datetime import datetime

from Orange.data import StringVariable, ContinuousVariable, TimeVariable

from ilpost import (
    IlPostClient,
    SortOrder,
    ContentType,
    DateRange,
)
from orangecontrib.text.util import create_corpus

RESULTS_PER_PAGE = 10
CONTENT_VAR_NAME = "Content"


class IlPostAPI:
    metas = [
        (
            partial(StringVariable, "Title"),
            lambda doc: doc.title,
        ),
        (
            partial(StringVariable, "Summary"),
            lambda doc: doc.summary,
        ),
        (
            partial(StringVariable, CONTENT_VAR_NAME),
            lambda doc: doc.content or "",
        ),
        (
            partial(StringVariable, "Highlight"),
            lambda doc: doc.highlight or "",
        ),
        (
            partial(StringVariable, "Category"),
            lambda doc: doc.category or "",
        ),
        (
            partial(StringVariable, "Tags"),
            lambda doc: ", ".join(doc.post_tag_text) if doc.post_tag_text else "",
        ),
        (
            partial(StringVariable, "Type"),
            lambda doc: doc.type,
        ),
        (
            partial(TimeVariable, "Publication Date", have_time=1, have_date=1),
            lambda doc: _parse_timestamp(doc.timestamp),
        ),
        (
            partial(StringVariable, "URL"),
            lambda doc: doc.link,
        ),
        (
            partial(ContinuousVariable, "Relevance Score", number_of_decimals=2),
            lambda doc: doc.score,
        ),
    ]

    text_features = ["Title", "Summary"]

    title_indices = [-1]  # Title

    def __init__(self, on_progress=None, should_break=None):
        self.client = IlPostClient()
        self.on_progress = on_progress or (lambda x, y: None)
        self.should_break = should_break or (lambda: False)
        self.results = []

    def search(
        self,
        query,
        content_type=None,
        date_range=None,
        sort=SortOrder.RELEVANCE,
        category=None,
        max_documents=100,
        include_paywalled=True,
        fetch_content=False,
    ):
        self.results = []
        hits = RESULTS_PER_PAGE

        first_page = self.client.search(
            query,
            page=1,
            hits=hits,
            sort=sort,
            content_type=content_type,
            category=category,
            date_range=date_range,
            fetch_content=fetch_content,
        )

        self._collect_docs(first_page.docs, include_paywalled)
        total = first_page.total
        pages_needed = min(
            first_page.total_pages,
            math.ceil(max_documents / hits),
        )
        self.on_progress(len(self.results), min(total, max_documents))

        for p in range(2, pages_needed + 1):
            if self.should_break():
                break
            if len(self.results) >= max_documents:
                break

            page_result = self.client.search(
                query,
                page=p,
                hits=hits,
                sort=sort,
                content_type=content_type,
                category=category,
                date_range=date_range,
                fetch_content=fetch_content,
            )
            self._collect_docs(page_result.docs, include_paywalled)
            self.on_progress(len(self.results), min(total, max_documents))

        self.results = self.results[:max_documents]

        if not self.results:
            return None

        return create_corpus(
            self.results,
            [],
            [],
            self.metas,
            self.title_indices,
            self.text_features,
            "Il Post",
        )

    def _collect_docs(self, docs, include_paywalled):
        for doc in docs:
            if not include_paywalled and doc.is_paywalled:
                continue
            self.results.append(doc)


def _parse_timestamp(ts):
    try:
        dt = datetime.fromisoformat(ts)
        return dt.timestamp()
    except (ValueError, TypeError):
        return 0.0
