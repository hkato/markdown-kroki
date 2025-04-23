import os

import markdown
from markdown_kroki import KrokiDiagramExtension

markdown_text = """
# Sample Markdown with Kroki Diagrams

## PlantUML

```plantuml theme="sketchy-outline"
Alice -> Bob: Hello Bob
Bob -> Alice: Hello Alice
```

## Mermaid

```mermaid theme="forest"
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob
    Bob->>Alice: Hello Alice
```
"""

html_output = markdown.markdown(
    markdown_text, extensions=[KrokiDiagramExtension(kroki_url='https://kroki.io', img_src='data')]
)

with open(os.path.splitext(__file__)[0] + '.html', 'w') as f:
    f.write(html_output)
