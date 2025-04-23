"""Diagram extension for Python-Markdown using Kroki"""

import base64
import re
from typing import Generator, List
import zlib

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
    IMG_TAG_ATTRIBUTES = [
        'alt',
        'width',
        'height',
        'class',
        'id',
        'style',
        'title',
    ]

    def __init__(self, md, config):
        super().__init__(md)
        self.kroki_url = config.get('kroki_url', self.KROKI_URL)
        self.img_src = config.get('img_src', 'data')

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
                code_block_options = {}
                if options:
                    for option in options.split():
                        key, _, value = option.partition('=')
                        code_block_options[key] = value
                continue

            elif re.search(self.DIAGRAM_BLOCK_END_RE, line):
                # Image format
                if 'format' in code_block_options:
                    format = code_block_options['format'].strip('"')
                    del code_block_options['format']
                    if format not in ['svg', 'png']:
                        format = 'svg'
                else:
                    format = 'svg'

                # img tag attributes and Kroki options
                img_tag_attributes = {}
                kroki_options = {}
                for option in code_block_options:
                    if option in self.IMG_TAG_ATTRIBUTES:
                        img_tag_attributes[option] = code_block_options[option]
                    else:
                        key = self._convert_mermaid_options_key(option)
                        kroki_options[key] = code_block_options[option].strip('"')

                img_src = self._get_img_src(diagram_code, language, format, kroki_options)
                if img_src:
                    # Build the <img> tag with extracted options
                    img_tag = f'<img src="{img_src}"'
                    for key, value in img_tag_attributes.items():
                        img_tag += f' {key}={value}'
                    img_tag += ' />'
                    html_string = img_tag
                break

            else:
                diagram_code = diagram_code + '\n' + line

        return html_string

    def _convert_mermaid_options_key(self, key: str) -> str:
        """Convert Mermaid options key to Kroki options key."""
        # https://docs.kroki.io/kroki/setup/diagram-options/#_mermaid
        key = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', key)
        key = re.sub('([a-z0-9])([A-Z])', r'\1-\2', key)
        key = key.replace('.', '_').lower()
        return key

    def _get_img_src(self, diagram_code: str, language: str, format: str, kroki_options: dict) -> str:
        """Convert diagram code to <img src>"""
        if self.img_src == 'data':
            # data URI
            img_src = self._get_img_src_data(diagram_code, language, format, kroki_options)
        elif self.img_src == 'link':
            # Direct link
            img_src = self._get_img_src_link(diagram_code, language, format, kroki_options)
        return img_src

    def _get_img_src_data(self, diagram_code: str, language: str, format: str, kroki_options: dict) -> str:
        """Convert diagram code to img src data URI"""
        base64image = self._get_base64image(diagram_code, language, format, kroki_options)
        img_src = f'data:{self.MIME_TYPES[format]};base64,{base64image}'
        return img_src

    def _get_img_src_link(self, diagram_code: str, language: str, format: str, kroki_options: dict) -> str:
        """Convert diagram code to img src direct link"""
        encoded_code = base64.urlsafe_b64encode(zlib.compress(diagram_code.encode('utf-8'), 9)).decode('ascii')
        option_list = []
        options = ''
        for key, value in kroki_options.items():
            option_list.append(f'{key}={value}')
        if option_list:
            options = '?' + '&'.join(option_list)
        # Kroki GET API
        kroki_url = f'{self.kroki_url}/{language}/{format}/{encoded_code}{options}'
        return kroki_url

    def _get_base64image(self, diagram_code: str, language: str, format: str, kroki_options: dict) -> str:
        """Convert diagram code to SVG/PNG using Kroki."""
        kroki_url = f'{self.kroki_url}/{language}/{format}'
        headers = {'Content-Type': 'text/plain'}
        for key, value in kroki_options.items():
            headers[f'Kroki-Diagram-Options-{key}'] = value

        response = requests.post(kroki_url, headers=headers, data=diagram_code, timeout=30)
        if response.status_code == 200:
            if format == 'svg':
                body = response.content.decode('utf-8')
                base64image = base64.b64encode(body.encode('utf-8')).decode('utf-8')
                return base64image
            if format == 'png':
                body = response.content
                base64image = base64.b64encode(body).decode('utf-8')
                return base64image
        return ''


class KrokiDiagramExtension(Extension):
    """Markdown Extension to support diagrams using Kroki."""

    def __init__(self, **kwargs):
        self.config = {
            'kroki_url': ['https://kroki.io', 'Base URL for the Kroki server.'],
            'img_src': ['data', 'Image source: data or link.'],
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
