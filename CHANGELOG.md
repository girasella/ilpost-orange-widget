# Changelog

## [0.2.0] - 2026-04-05

### Added
- **Full article content download**: selecting *Content (max 100 articles)* in the Text includes panel now fetches the full article body. The max documents spinner is automatically capped to 100 when this option is active.
- **Select All checkbox**: added a *Select All* checkbox at the top of the Text includes panel to check or uncheck all fields at once. Shows a partial state when only some fields are selected.

### Changed
- The *Download full article content* checkbox has been removed. Content downloading is now controlled by the *Content (max 100 articles)* entry in the Text includes panel.
- The output corpus now contains only the columns selected in Text includes (Publication Date and Relevance Score are always included). Previously all columns were always present in the output.
- The *Content* corpus column is named `Content`; the corresponding checkbox label reads *Content (max 100 articles)* to make the cap visible in the UI.
- Max documents spinner now allows any value from 1 to 1000 (previously stepped in increments of 10 with a minimum of 10).

### Fixed
- Max documents setting was ignored when full content download was enabled — the widget always fetched 100 documents regardless of the spinner value.

## [0.1.0] - 2026-04-02

Initial release.

- Search Il Post by keyword with filters for content type, date range, sort order, and editorial category.
- Options to set max documents (up to 1000) and include/exclude paywalled content.
- Configurable text features (Title, Summary, Highlight, Category, Tags) via a checklist.
- Outputs an Orange3 `Corpus` compatible with all orange3-text widgets.
