"""
Markdown Kroki Plugin for MkDocs (Experimental)
Embed external diagrams in your MkDocs documentation with Kroki using the ![]() syntax.
"""

import os
import re
from typing import Tuple

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from .kroki import KrokiServer


class KrokiDiagramPlugin(BasePlugin):
    DIAGRAM_LIST = [
        # Draw.io
        {'ext': 'drawio', 'language': 'diagramsnet'},
        {'ext': 'drawio.svg', 'language': 'diagramsnet'},
        # PlantUML
        {'ext': 'pu', 'language': 'plantuml'},
        {'ext': 'puml', 'language': 'plantuml'},
        # Mermaid
        {'ext': 'mmd', 'language': 'mermaid'},
        {'ext': 'mermaid', 'language': 'mermaid'},
        # Graphviz
        {'ext': 'dot', 'language': 'graphviz'},
        {'ext': 'gv', 'language': 'graphviz'},
        # Excalidraw
        {'ext': 'excalidraw', 'language': 'excalidraw'},
        {'ext': 'excalidraw.json', 'language': 'excalidraw'},
    ]

    config_scheme = (
        ('kroki_url', config_options.Type(str, default='https://kroki.io')),
        ('format', config_options.Choice(['svg', 'png'], default='svg')),
        ('img_src', config_options.Choice(['data', 'link'], default='data')),
    )

    def on_config(self, config, **kwargs):
        """Called when the plugin is loaded."""
        self.kroki_url = self.config['kroki_url']
        self.format = self.config['format']
        self.img_src = self.config['img_src']
        self.kroki_server = KrokiServer(self.kroki_url, self.img_src)
        return config

    def on_page_markdown(self, markdown: str, page: Page, config, files: Files):
        """Called when the page is being processed."""

        def replace_diagram_to_image_src(match):
            alt_text = match.group('alt')
            diagram_file_path = match.group('src')

            is_supported, language = self._check_file_type(diagram_file_path)

            if is_supported:
                # Handle absolute and relative paths
                docs_dir = config['docs_dir']
                md_file_dir = os.path.dirname(page.file.abs_src_path)
                if diagram_file_path.startswith('/'):
                    abs_diagram_file_path = os.path.join(docs_dir, diagram_file_path[1:])
                else:
                    abs_diagram_file_path = os.path.join(md_file_dir, diagram_file_path)

                try:
                    with open(abs_diagram_file_path, 'r') as f:
                        diagram_code = f.read()

                    src = self.kroki_server.get_img_src(diagram_code, language, self.format, {})
                    html = f'<img alt="{alt_text}" src="{src}" />'
                    return html
                except FileNotFoundError:
                    return f'<p style="color:red;">Error: file not found: {abs_diagram_file_path}</p>'
                except Exception as e:
                    return f'<p style="color:red;">Error processing file {abs_diagram_file_path}: {e}</p>'
            return match.group(0)

        pattern = re.compile(r'!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]*)\)', re.IGNORECASE)
        return re.sub(pattern, replace_diagram_to_image_src, markdown)

    def _check_file_type(self, file_path: str) -> Tuple[bool, str]:
        """Check if the file type is supported."""
        language = ''
        is_supported = False
        for diagram in self.DIAGRAM_LIST:
            if file_path.lower().endswith(diagram['ext']):
                is_supported = True
                language = diagram['language']
                break
        return is_supported, language
