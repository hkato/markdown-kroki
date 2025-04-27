# [markdown-kroki](https://hkato.github.io/markdown-kroki/)

[![PyPI version](https://img.shields.io/pypi/v/markdown-kroki)](https://pypi.org/project/markdown-kroki/)
![License](https://img.shields.io/pypi/l/markdown-kroki)
![Python versions](https://img.shields.io/pypi/pyversions/markdown-kroki)

Diagram extension for [Python-Markdown][python-markdown] using [Kroki server][kuroki].

This extension converts various diagram code blocks into Base64 encoded [data: URI][data-uri] or direct image link.
This enables PDF generation with tools like [MkDocs to PDF][mkdocs-to-pdf]/[WeasyPrint][wasyprint]
without requiring JavaScript(e.g. [Mermaid][mermaid])

## Install

```sh
pip install markdown-kroki
```

## Requirements

### Internet access to the public Kroki server

Default setting with no options.

### Self-Managed Kroki server (recommended)

Here is a sample Docker Compose file.

ref. Kroki.io > [Install](https://kroki.io/#install) > [Using Docker or Podman](https://docs.kroki.io/kroki/setup/use-docker-or-podman/)

```sh
docker compose up -d
```

> The default port used by MkDocs (`mkdocs serve`) may conflict with the default
> port of a Dockerized Kroki instance.
> Consequently, you will need to change the port configuration for one of them.

## Usage

````md
```{diagram language} formant=[svg|png] {img tag attribute}="value" {diagram option}="value"
```
````

- format (optional): Output image format default to svg
- img tag attribute (optional): alt, width, height, class, id, style, title
- diagram option (optional): refer to [Diagram options](https://docs.kroki.io/kroki/setup/diagram-options/)

### [MkDocs][mkdocs] Integration

```yaml
# mkdocs.yml
markdown_extensions:
  - markdown_kroki:
      kroki_url: http://localhost:18000  # default: https://kroki.io
      img_src: link                      # default: data/data URI, link/direct link
```

### [Pelican][pelican] Integration

```py
# pelicanconf.py
MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
        'markdown_kroki': {                         # Add these
            'kroki_url': 'http://localhost:18000',
            'img_src': 'link'
        },
    },
    'output_format': 'html5',
}
```

### Python code

````python
import markdown
from markdown_kroki import KrokiDiagramExtension

markdown_text = """```plantuml format="svg" theme="sketchy-outline" width="300"
@startuml
Alice -> Bob: Authentication Request
Bob --> Alice: Authentication Response
@enduml
```"""

html_output = markdown.markdown(markdown_text, extensions=[
                                KrokiDiagramExtension(kroki_url='https://kroki.io')])

print(html_output)
````

```html
<p><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLXJvbGVkZXNjcmlwdGlvbj0ic2VxdWVuY2UiIHJvbGU
9ImdyYXBoaWNzLWRvY3VtZW50IGRvY3VtZW50IiB2aWV3Qm94PSItNTAgLTEwIDc1MCA1NzQiIHN0eWxlPSJtYXgtd2lkd
Gg6IDc1MHB4OyBiYWNrZ3JvdW5kLWNvbG9yOiB3aGl0ZTsiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk
...
...
...
IHgxPSIyNzYiLz48L3N2Zz4=" width="300" ></p>
```

## Process flow

### data URI

```mermaid
sequenceDiagram
    participant application as MkDocs, Pelican<br/>or your application
    participant markdown as Python Markdown
    participant extension as KrokiDiagramExtension
    participant engine as Kroki Server

    application->>markdown: Markdown + Diagrams
    markdown->>extension: Preprocessor
    extension->>engine: Diagram code
    engine-->>engine: Convert
    engine-->>extension: Image Data
    extension-->>extension: Base64 encode
    extension-->>markdown: Markdown + data URI image
    markdown-->>application: HTML + data URI image
```

### Direct link (GET API)

```mermaid
sequenceDiagram
    participant application as MkDocs, Pelican<br/>or your application
    participant markdown as Python Markdown
    participant extension as KrokiDiagramExtension
    participant engine as Kroki Server

    application->>markdown: Markdown + Diagrams
    markdown->>extension: Preprocessor
    extension-->>extension: Encoded code<br/>base64+deflate
    extension-->>markdown: Markdown + Kroki direct link
    markdown-->>application: HTML + Kroki direct kink
    application->>engine: GET API<br/><img src="http[s]">
    engine-->>application: Image data
```

<!-- Links -->

[python-markdown]: https://python-markdown.github.io/
[kuroki]: https://kroki.io/
[data-uri]: https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Schemes/data
[mkdocs-to-pdf]: https://mkdocs-to-pdf.readthedocs.io/
[wasyprint]: https://weasyprint.org/
[mermaid]: https://mermaid.js.org/
[mkdocs]: https://www.mkdocs.org/
[pelican]: https://getpelican.com/
