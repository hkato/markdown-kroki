import base64
import urllib.request
import zlib

process_flow_diagram_file = 'process_flow_diagram.svg'
process_flow_diagram_code = """
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
"""

encoded_image = base64.urlsafe_b64encode(zlib.compress(process_flow_diagram_code.encode('utf-8'), 9)).decode('ascii')

with urllib.request.urlopen(f'https://kroki.io/mermaid/svg/{encoded_image}') as response:
    body = response.read().decode('utf-8')
    with open(process_flow_diagram_file, 'wb') as f:
        f.write(body.encode('utf-8'))
