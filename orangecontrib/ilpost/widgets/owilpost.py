from AnyQt.QtCore import Qt
from AnyQt.QtWidgets import QApplication

from Orange.data import StringVariable, Domain
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Msg
from Orange.widgets import gui
from Orange.widgets.widget import Output

from orangecontrib.text.corpus import Corpus
from orangecontrib.text.widgets.utils import CheckListLayout, QueryBox, asynchronous

from ilpost import SortOrder, ContentType, DateRange
from orangecontrib.ilpost.ilpost_api import IlPostAPI, CONTENT_VAR_NAME

CONTENT_CHECKBOX_LABEL = "Content (max 100 articles)"

CONTENT_TYPE_LABELS = [
    ("All", None),
    ("Articles", ContentType.ARTICLES),
    ("Podcasts", ContentType.PODCASTS),
    ("Newsletters", ContentType.NEWSLETTERS),
]

DATE_RANGE_LABELS = [
    ("All time", DateRange.ALL_TIME),
    ("Past year", DateRange.PAST_YEAR),
    ("Past 30 days", DateRange.PAST_30_DAYS),
]

SORT_ORDER_LABELS = [
    ("Relevance", SortOrder.RELEVANCE),
    ("Newest", SortOrder.NEWEST),
    ("Oldest", SortOrder.OLDEST),
]


class OWIlPost(OWWidget):
    name = "Il Post"
    description = "Fetch articles from Il Post."
    icon = "icons/IlPost.jpg"
    priority = 130
    keywords = "il post, articles, italy, italian, newspaper"

    class Outputs:
        corpus = Output("Corpus", Corpus)

    want_main_area = False
    resizing_enabled = False

    recent_queries = Setting([])
    content_type_idx = Setting(0)
    date_range_idx = Setting(0)
    sort_order_idx = Setting(0)
    filter_category = Setting("")
    MAX_DOCUMENTS_WITH_CONTENT = 100

    max_documents = Setting(100)
    include_paywalled = Setting(True)

    attributes = [
        CONTENT_CHECKBOX_LABEL if part.args[0] == CONTENT_VAR_NAME else part.args[0]
        for part, _ in IlPostAPI.metas
        if part.func is StringVariable
    ]
    text_includes = Setting(list(IlPostAPI.text_features))

    class Warning(OWWidget.Warning):
        no_text_fields = Msg("Text features are inferred when none are selected.")

    class Error(OWWidget.Error):
        no_query = Msg("Please provide a query.")
        search_error = Msg("Search failed: {}")
        no_results = Msg("No results found.")

    def __init__(self):
        super().__init__()
        self.corpus = None
        self.api = None
        self.output_info = ""

        # Query
        query_box = gui.widgetBox(self.controlArea, "Query")
        self.query_box = QueryBox(
            query_box, self, self.recent_queries, callback=self.new_query_input
        )

        # Filters
        filter_box = gui.widgetBox(self.controlArea, "Filters")

        gui.comboBox(
            filter_box,
            self,
            "content_type_idx",
            label="Content type:",
            items=[label for label, _ in CONTENT_TYPE_LABELS],
            orientation=Qt.Horizontal,
        )

        gui.comboBox(
            filter_box,
            self,
            "date_range_idx",
            label="Date range:",
            items=[label for label, _ in DATE_RANGE_LABELS],
            orientation=Qt.Horizontal,
        )

        gui.comboBox(
            filter_box,
            self,
            "sort_order_idx",
            label="Sort by:",
            items=[label for label, _ in SORT_ORDER_LABELS],
            orientation=Qt.Horizontal,
        )

        gui.lineEdit(
            filter_box,
            self,
            "filter_category",
            label="Category:",
            placeholderText="e.g. politica, cultura (articles only)",
            orientation=Qt.Horizontal,
        )

        # Options
        options_box = gui.widgetBox(self.controlArea, "Options")

        self.max_documents_spin = gui.spin(
            options_box,
            self,
            "max_documents",
            minv=1,
            maxv=1000,
            step=1,
            label="Max documents:",
        )

        gui.checkBox(
            options_box,
            self,
            "include_paywalled",
            label="Include paywalled content",
        )

        # Text includes features
        self.controlArea.layout().addWidget(
            CheckListLayout(
                "Text includes",
                self,
                "text_includes",
                self.attributes,
                cols=2,
                callback=self._on_text_includes_changed,
            )
        )

        self._on_text_includes_changed()

        # Output
        info_box = gui.hBox(self.controlArea, "Output")
        gui.label(info_box, self, "Articles: %(output_info)s")

        # Buttons
        self.button_box = gui.hBox(self.controlArea)
        self.search_button = gui.button(
            self.button_box, self, "Search", self.start_stop, focusPolicy=Qt.NoFocus
        )

    @property
    def fetch_content(self):
        return CONTENT_CHECKBOX_LABEL in self.text_includes

    def _on_text_includes_changed(self):
        if self.fetch_content:
            self.max_documents_spin.setMaximum(self.MAX_DOCUMENTS_WITH_CONTENT)
            self.max_documents = min(
                self.max_documents, self.MAX_DOCUMENTS_WITH_CONTENT
            )
        else:
            self.max_documents_spin.setMaximum(1000)
        self.set_text_features()

    def new_query_input(self):
        self.search.stop()
        self.search()

    def start_stop(self):
        if self.search.running:
            self.search.stop()
        else:
            self.query_box.synchronize(silent=True)
            self.run_search()

    def run_search(self):
        self.Error.no_query.clear()
        self.Error.search_error.clear()
        self.Error.no_results.clear()

        if not self.recent_queries:
            self.Error.no_query()
            return

        self.search()

    @asynchronous
    def search(self):
        self.api = IlPostAPI(
            on_progress=self.progress_with_info,
            should_break=self.search.should_break,
        )

        _, content_type = CONTENT_TYPE_LABELS[self.content_type_idx]
        _, date_range = DATE_RANGE_LABELS[self.date_range_idx]
        _, sort_order = SORT_ORDER_LABELS[self.sort_order_idx]
        category = self.filter_category.strip() or None

        return self.api.search(
            self.recent_queries[0],
            content_type=content_type,
            date_range=date_range,
            sort=sort_order,
            category=category,
            max_documents=self.max_documents,
            include_paywalled=self.include_paywalled,
            fetch_content=self.fetch_content,
        )

    @search.callback(should_raise=False)
    def progress_with_info(self, n_retrieved, n_all):
        self.progressBarSet(100 * (n_retrieved / n_all if n_all else 1))
        self.output_info = "{}/{}".format(n_retrieved, n_all)

    @search.on_start
    def on_start(self):
        self.progressBarInit()
        self.search_button.setText("Stop")
        self.Outputs.corpus.send(None)

    @search.on_result
    def on_result(self, result):
        self.search_button.setText("Search")
        self.progressBarFinished()

        if result is None:
            self.output_info = "0"
            self.Error.no_results()
            self.corpus = None
            self.Outputs.corpus.send(None)
            return

        self.corpus = result
        self.output_info = str(len(result))
        self.set_text_features()

    def set_text_features(self):
        self.Warning.no_text_fields.clear()
        if not self.text_includes:
            self.Warning.no_text_fields()

        if self.corpus is not None:
            # Map checkbox labels to actual variable names
            selected_var_names = {
                CONTENT_VAR_NAME if label == CONTENT_CHECKBOX_LABEL else label
                for label in self.text_includes
            }
            # Keep non-string metas always; filter string metas to selected only
            metas = [
                var for var in self.corpus.domain.metas
                if not isinstance(var, StringVariable) or var.name in selected_var_names
            ]
            domain = Domain(
                self.corpus.domain.attributes,
                self.corpus.domain.class_vars,
                metas,
            )
            filtered = self.corpus.from_table(domain, self.corpus)
            text_vars = [var for var in filtered.domain.metas if var.name in selected_var_names]
            filtered.set_text_features(text_vars or None)
            self.Outputs.corpus.send(filtered)

    def send_report(self):
        if self.corpus:
            _, content_type = CONTENT_TYPE_LABELS[self.content_type_idx]
            self.report_items(
                (
                    ("Query", self.recent_queries[0]),
                    ("Content type", content_type.value if content_type else "All"),
                    ("Max documents", self.MAX_DOCUMENTS_WITH_CONTENT if self.fetch_content else self.max_documents),
                    ("Download full content", "Yes" if self.fetch_content else "No"),
                    ("Text includes", ", ".join(self.text_includes)),
                    ("Output", self.output_info or "Nothing"),
                )
            )


if __name__ == "__main__":
    app = QApplication([])
    widget = OWIlPost()
    widget.show()
    app.exec()
    widget.saveSettings()
