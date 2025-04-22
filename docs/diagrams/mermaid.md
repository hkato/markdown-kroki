# Mermaid

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Bob->>Alice: Hi Alice
    Alice->>Bob: Hi Bob
```

## with options

```mermaid theme="forest"
sequenceDiagram
    participant Alice
    participant Bob
    Bob->>Alice: Hi Alice
    Alice->>Bob: Hi Bob
```

## graph syntax

!!! warning
    When generating PDF, text within the `graph` syntax doesn't get output in WeasyPrint.
    However, it does appear when using Playwright/Chromium.
    As a countermeasure for WeasyPrint limitations, use PNG images.

```mermaid format="png" height="400"
graph TD
  A[ Anyone ] -->|Can help | B( Go to github.com/yuzutech/kroki )
  B --> C{ How to contribute? }
  C --> D[ Reporting bugs ]
  C --> E[ Sharing ideas ]
  C --> F[ Advocating ]
```
