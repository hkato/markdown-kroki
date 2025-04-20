"""Diagram extension for Python-Markdown using Kroki"""

import base64
import re
from typing import Generator, List

import requests
from markdown import Extension
from markdown.preprocessors import Preprocessor


class KrokiDiagramProcessor(Preprocessor):
    """Preprocessor to convert diagram code blocks to SVG/PNG image Data URIs."""

    DIAGRAM_LIST = '|'.join(
        [
            'actdiag',
            'blockdiag',
            'bytefield',
            'c4plantuml',
            'd2',
            'dbml',
            'ditaa',
            'erd',
            'excalidraw',
            'graphviz',
            'mermaid',
            'nomnoml',
            'nwdiag',
            'packetdiag',
            'pikchr',
            'plantuml',
            'rackdiag',
            'seqdiag',
            'structurizr',
            'svgbob',
            'symbolator',
            'tikz',
            'vegalite',
            'vega',
            'wavedrom',
            'wireviz',
            'plantuml',  # FIXME: temporary fix...
        ]
    )
    DIAGRAM_BLOCK_START_RE = re.compile(r'^\s*```(?P<language>' + DIAGRAM_LIST + r'\w+)(?:\s+(?P<options>.+))?')
    DIAGRAM_BLOCK_END_RE = re.compile(r'^\s*```')

    KROKI_URL = 'https://kroki.io'

    MIME_TYPES = {
        'svg': 'image/svg+xml',
        'png': 'image/png',
    }

    def __init__(self, md, config):
        super().__init__(md)
        self.kroki_url = config.get('kroki_url', self.KROKI_URL)

    def run(self, lines: List[str]) -> List[str]:
        return list(self._parse_diagram_block(lines))

    def _parse_diagram_block(self, lines: List[str]) -> Generator:
        """Parse diagram code block"""
        is_in_diagram_block = False
        block_lines: List[str] = []

        for line in lines:
            if is_in_diagram_block:
                block_lines.append(line)
                if self.DIAGRAM_BLOCK_END_RE.match(line):
                    is_in_diagram_block = False
                    line = self._diagram_block_to_html(block_lines)
                    block_lines = []
                    yield line
            else:
                if self.DIAGRAM_BLOCK_START_RE.match(line):
                    is_in_diagram_block = True
                    block_lines.append(line)
                else:
                    yield line

    def _diagram_block_to_html(self, lines: List[str]) -> str:
        """Convert diagram code block to HTML"""
        diagram_code = ''
        html_string = ''

        for line in lines:
            diagram_match = re.search(self.DIAGRAM_BLOCK_START_RE, line)
            if diagram_match:
                language = diagram_match.group('language')
                options = diagram_match.group('options')
                option_dict = {}
                if options:
                    for option in options.split():
                        key, _, value = option.partition('=')
                        option_dict[key] = value
                continue

            elif re.search(self.DIAGRAM_BLOCK_END_RE, line):
                if 'image' in option_dict:
                    image_type = option_dict['image']
                    del option_dict['image']
                    if image_type not in ['svg', 'png']:
                        image_type = 'svg'
                else:
                    image_type = 'svg'

                base64image = self._get_base64image(diagram_code, language, image_type)
                if base64image:
                    # Build the <img> tag with extracted options
                    img_tag = f'<img src="data:{self.MIME_TYPES[image_type]};base64,{base64image}"'
                    for key, value in option_dict.items():
                        img_tag += f' {key}={value}'
                    img_tag += ' />'
                    html_string = img_tag
                break

            else:
                diagram_code = diagram_code + '\n' + line

        return html_string

    def _get_base64image(self, diagram_code: str, language: str, image_type: str) -> str:
        """Convert diagram code to SVG/PNG using Kroki."""
        kroki_url = f'{self.kroki_url}/{language}/{image_type}'
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(kroki_url, headers=headers, data=diagram_code, timeout=30)
        if response.status_code == 200:
            if image_type == 'svg':
                body = response.content.decode('utf-8')
                base64image = base64.b64encode(body.encode('utf-8')).decode('utf-8')
                return base64image
            if image_type == 'png':
                body = response.content
                base64image = base64.b64encode(body).decode('utf-8')
                return base64image
        return ''


class KrokiDiagramExtension(Extension):
    """Markdown Extension to support diagrams using Kroki."""

    def __init__(self, **kwargs):
        self.config = {
            'kroki_url': ['https://kroki.io', 'Base URL for the Kroki server.'],
        }
        super().__init__(**kwargs)
        self.extension_configs = kwargs

    def extendMarkdown(self, md):
        config = self.getConfigs()
        final_config = {**config, **self.extension_configs}
        kroki_diagram_preprocessor = KrokiDiagramProcessor(md, final_config)
        md.preprocessors.register(kroki_diagram_preprocessor, 'markdown_kroki', 50)


# pylint: disable=C0103
def makeExtension(**kwargs):
    """Create an instance of the KrokiDiagramExtension."""
    return KrokiDiagramExtension(**kwargs)
