# MkDocs Plugin (Experimental)

Furthermore, when used as an MkDocs plugin, it offers the capability
to load diagrams from external files.

## Usage

### Markdown

````markdown
![alt text](diagram file)
````

### mkdocs.yml

```yaml
plugins:
  - kroki_diagrams:
      kroki_url: http://localhost:18000     # default: https://kroki.io
      format: png                           # default: svg
      img_src: link                         # default: data
```

## Samples

[:link: Markdown code](https://github.com/hkato/markdown-kroki/tree/main/docs/experimental)

### Draw.io

![Drawio sample](sample.drawio)

### Excaldraw

![Excalidraw sample](sample.excalidraw)
