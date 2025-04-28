"""Test KrokiServer class."""

import pytest
import requests

from markdown_kroki.kroki import KrokiServer

test_diagram_plantuml = """skinparam ranksep 20
skinparam dpi 125
skinparam packageTitleAlignment left

rectangle "Main" {
  (main.view)
  (singleton)
}
rectangle "Base" {
  (base.component)
  (component)
  (model)
}
rectangle "<b>main.ts</b>" as main_ts

(component) ..> (base.component)
main_ts ==> (main.view)
(main.view) --> (component)
(main.view) ...> (singleton)
(singleton) ---> (model)"""

test_diagram_mermaid = """graph TD
  A[ Anyone ] -->|Can help | B( Go to github.com/yuzutech/kroki )
  B --> C{ How to contribute? }
  C --> D[ Reporting bugs ]
  C --> E[ Sharing ideas ]
  C --> F[ Advocating ]
"""


@pytest.mark.parametrize(
    'diagram_code, language, format, options, expected_url',
    [
        (
            test_diagram_plantuml,
            'plantuml',
            'svg',
            {'theme': 'forest'},
            'data:image/svg+xml;base64,ZmFrZV9pbWFnZV9kYXRh',
        ),
        (
            test_diagram_mermaid,
            'mermaid',
            'png',
            {'theme': 'base'},
            'data:image/png;base64,ZmFrZV9pbWFnZV9kYXRh',
        ),
    ],
)
def test_get_img_src_data(mocker, diagram_code, language, format, options, expected_url):
    """Test the get_img_src method."""
    # Mock the requests.post method to return a fake response
    mock_response = mocker.Mock(spec=requests.Response)
    mock_response.content = b'fake_image_data'  # echo -n 'fake_image_data' | base64
    mock_response.status_code = 200
    mocker.patch('requests.post', return_value=mock_response)

    kroki = KrokiServer('https://kroki.io', 'data')
    result = kroki.get_img_src(diagram_code, language, format, options)
    assert result == expected_url, f'Expected data URI, but got {result}'


@pytest.mark.parametrize(
    'diagram_code, language, format, options, expected_url',
    [
        (
            test_diagram_plantuml,
            'plantuml',
            'svg',
            {'theme': 'sketchy-outline'},
            'https://kroki.io/plantuml/svg/eNpljzEPgjAQhff-iguTDFQlcYMmuru5mwNO0tCWhjY6GP-7LRJTdHvv7r67d26QxuKEGiY0gyML5Y65b7GzEvblIalYbAfs6SK9oqOSvdFkPCi6ecYmaj2aXhFkZ5QmgycD2Ogg-V3SI4_OyTjgR5OzVwqc0NECNEHydtR2NGH3TK2dHjtSP3zViPmQd9W2ERmgg-iv3jGW4MC5-L-wTEJdi1XeRENRiFWOtMfnrclriQ5gJD-Z3x9beAM=?theme=sketchy-outline',
        ),
        (
            test_diagram_mermaid,
            'mermaid',
            'png',
            {'theme': 'forest'},
            'https://kroki.io/mermaid/png/eNpNzr0OgjAcBPCdp7hRB-QNNHz4Masb6VBK0zZg_6S2GhTf3cJgnH93l1OODxrXKgHyGrkdyUowpOl2KrmFlv2ACcUKR4InKON1aDaCbtkYXsFLobPOUWewjgvF3EP5xomec1qQ9c40MbbDJ3q5eFXjLAdy3liFJqg72M_2NS6au1lMK_k_HeK99kGCLz2WfAHnUzg5?theme=forest',
        ),
    ],
)
def test_get_img_src_link(diagram_code, language, format, options, expected_url):
    """Test the get_img_src method."""
    kroki = KrokiServer('https://kroki.io', 'link')
    result = kroki.get_img_src(diagram_code, language, format, options)
    assert result == expected_url, f'Expected data URI, but got {result}'


@pytest.mark.parametrize(
    'input_options, expected_options',
    [
        ({'theme': 'base'}, {'theme': 'base'}),
        ({'fontFamily': 'courier'}, {'font-family': 'courier'}),
        ({'maxTextSize': '50'}, {'max-text-size': '50'}),
        ({'er.titleTopMargin': '100'}, {'er_title-top-margin': '100'}),
        ({'gantt.displayMode': 'compact'}, {'gantt_display-mode': 'compact'}),
    ],
)
def test_convert_mermaid_options_key(input_options, expected_options):
    """Test the conversion of mermaid options keys."""
    kroki = KrokiServer('https://kroki.io', 'data')
    result = kroki._convert_mermaid_options_key(input_options)
    assert result == expected_options, f'Expected {expected_options}, but got {result}'
