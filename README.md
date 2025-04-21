# [markdown-kroki](https://hkato.github.io/markdown-kroki/)

Diagram extension for [Python-Markdown][python-markdown] using [Kroki server][kuroki].

This extension converts various diagram code blocks into Base64 encoded [data: URI][data-uri].
This enables PDF generation with tools like [MkDocs to PDF][mkdocs-to-pdf]/[WeasyPrint][wasyprint] without requiring JavaScript, even during web browsing.

[mermaid]: https://mermaid.js.org/
[python-markdown]: https://python-markdown.github.io/
[kuroki]: https://kroki.io/
[data-uri]: https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Schemes/data
[mkdocs-to-pdf]: https://mkdocs-to-pdf.readthedocs.io/
[wasyprint]: https://weasyprint.org/

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

!!! note
    The default port used by MkDocs (`mkdocs serve`) may conflict with the default port of a Dockerized Kroki instance.
    Consequently, you will need to change the port configuration for one of them.

## Usage

### MkDocs Integration

```yaml
# mkdocs.yml
markdown_extensions:
  - markdown_kroki:
      kroki_url: http://localhost:18000  # default: https://kroki.io
```

### Python code

````python
import markdown
from markdown_kroki import KrokiDiagramExtension

markdown_text = """```plantuml format="svg" width="300"
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
IHgxPSIyNzYiLz48L3N2Zz4=" ></p>
```

## Process flow

```mermaid
sequenceDiagram
    participant application as Application<br/>(eg MkDocs)
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
