# Orange3 Il Post Widget

An [Orange3](https://orangedatamining.com/) add-on widget for fetching articles, podcasts, and newsletters from the Italian online newspaper [Il Post](https://www.ilpost.it/). The widget queries the Il Post search API and outputs a `Corpus` ready for text mining workflows.

## User Interface

![Il Post Orange Widget GUI](https://github.com/girasella/ilpost-orange-widget/raw/master/image.png)

## Installation

```bash
pip install orange3-ilpost
```

The package requires **Orange3** and **orange3-text** to be installed. The Il Post API wrapper ([ilpost-api-wrapper](https://pypi.org/project/ilpost-api-wrapper/)) is installed automatically as a dependency.

## Usage

After installation, the **Il Post** category will appear in the Orange Canvas widget toolbox.

1. Drag the **Il Post** widget onto the canvas.
2. Type a search query in the *Query* field and press Enter or click **Search**.
3. Adjust the filters as needed (see below).
4. Connect the widget output to any text mining widget (e.g. *Corpus Viewer*, *Word Cloud*, *Topic Modelling*).

### Controls

| Control | Description |
|---|---|
| **Query** | Search term. Keeps a history of recent queries. |
| **Content type** | Filter by *All*, *Articles*, *Podcasts*, or *Newsletters*. |
| **Date range** | Filter by *All time*, *Past year*, or *Past 30 days*. |
| **Sort by** | Sort results by *Relevance*, *Newest*, or *Oldest*. |
| **Category** | Optional editorial category filter (e.g. `politica`, `cultura`). Applies to articles only. |
| **Max documents** | Maximum number of results to retrieve (1–1000, capped at 100 when *Content* is selected). |
| **Include paywalled content** | When unchecked, subscriber-only results are excluded. |
| **Text includes** | Choose which fields are included in the output corpus and used as text features for analysis. Use **Select All** to check or uncheck all fields at once. Selecting *Content (max 100 articles)* also downloads the full article body (capped at 100 documents). |

### Output

The widget outputs a `Corpus` with the following metadata columns:

| Field | Type | Description |
|---|---|---|
| Title | String | Article/episode title |
| Summary | String | Short description |
| Content | String | Full article body (only when *Content* is selected in Text includes) |
| Highlight | String | Search snippet with matched terms |
| Category | String | Editorial category |
| Tags | String | Comma-separated topic tags |
| Type | String | Content type (`post`, `episodes`, `newsletter`) |
| Publication Date | Time | Publication timestamp (Italian local time) |
| URL | String | Link to the full content |
| Relevance Score | Continuous | Search relevance score (0.0 when sorted by date) |

Only the columns selected in **Text includes** appear in the output corpus (Publication Date and Relevance Score are always included).

### Example workflow

```
[Il Post] → [Corpus Viewer]
[Il Post] → [Word Cloud]
[Il Post] → [Topic Modelling]
[Il Post] → [Sentiment Analysis]
```

## Requirements

- Python 3.9+
- Orange3
- orange3-text
- [ilpost-api-wrapper](https://pypi.org/project/ilpost-api-wrapper/)

## License

MIT
