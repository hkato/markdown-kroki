import base64
import urllib.request
import zlib

figure = {
    'process_flow_diagram_data.svg': """
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
""",
    'process_flow_diagram_link.svg': """
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
""",
}

for filename, diagram_code in figure.items():
    encoded_image = base64.urlsafe_b64encode(zlib.compress(diagram_code.encode('utf-8'), 9)).decode('ascii')
    with urllib.request.urlopen(f'https://kroki.io/mermaid/svg/{encoded_image}') as response:
        body = response.read().decode('utf-8')
        with open(filename, 'wb') as f:
            f.write(body.encode('utf-8'))
