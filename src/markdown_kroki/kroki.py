"""
KrokiServer is a class that provides methods to generate diagrams from text using the Kroki API.
It supports various diagram types and formats, including SVG and PNG.
It can generate data URIs or direct links to the generated diagrams.
"""

import base64
import re
import zlib

import requests


class KrokiServer:
    """
    KrokiServer is a class that represents a Kroki server.
    It provides methods to generate diagrams from text using the Kroki API.
    """

    MIME_TYPES = {
        'svg': 'image/svg+xml',
        'png': 'image/png',
    }

    def __init__(self, kroki_url: str, img_src: str):
        """ "
        Initialize the KrokiServer with the given URL and image source type.
        :param kroki_url: The URL of the Kroki server.
        :param img_src: The type of image source ('data' or 'link').
        """
        self.kroki_url = kroki_url
        self.img_src = img_src

    def get_img_src(self, diagram_code: str, language: str, format: str, kroki_options: dict) -> str:
        """
        Generate the image source URL or data URI for the given diagram code.
        :param diagram_code: The code for the diagram.
        :param language: The language of the diagram (e.g., 'mermaid', 'plantuml').
        :param format: The format of the image (e.g., 'svg', 'png').
        :param kroki_options: Additional options for the Kroki API.
        :return: The image source URL or data URI.
        """
        kroki_options = self._convert_mermaid_options_key(kroki_options)
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
        """Convert diagram code to img src link"""
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
        """Convert diagram code to base64 image."""
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

    def _convert_mermaid_options_key(self, options: dict) -> dict:
        """Convert Mermaid options key to Kroki options key."""
        # https://docs.kroki.io/kroki/setup/diagram-options/#_mermaid
        converted_options = {}
        for key, value in options.items():
            key = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', key)
            key = re.sub('([a-z0-9])([A-Z])', r'\1-\2', key)
            key = key.replace('.', '_').lower()
            converted_options[key] = value
        return converted_options
