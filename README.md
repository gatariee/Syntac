a quick and dirty templating solution for creating cheatsheets quickly and easily

```bash
export FLASK_APP="app:init"
export FLASK_ENV=development
export FLASK_RUN_HOST='0.0.0.0'
flask run
```

[http://127.0.0.1:5000](http://127.0.0.1:5000) will be the default URL.

![](https://i.gyazo.com/f07200e1a91b83d102be5a423a68c421.png)

## making connectors

each connector is a `@register_module`, each connector can have an unlimited amount of `@sub_module`. for more examples, see [connectors](./connectors/)

```python
from .base import Module, register_module, sub_module
import textwrap


def wrap_code(template: str, /, **ctx) -> str:
    dedented = textwrap.dedent(template).strip()
    return dedented.format(**ctx)


@register_module
class Demo(Module):
    name = "Demo"
    description = ""

    @sub_module("Python - Hello World")
    def py_hello_world(self, code: str = "Hello, World!") -> str:
        return wrap_code(
            f"""
            print("{code}")
            """
        )

    @sub_module("Python - Add Numbers (Integers)")
    def py_add_numbers(self, a: int = 1, b: int = 1) -> str:
        return int(a) + int(b)

    @sub_module("Python - Add Numbers (Floats)")
    def py_add_numbers_float(self, a: float = 1.0, b: float = 1.0) -> str:
        return float(a) + float(b)

    @sub_module("rot13")
    def rot13(self, text: str = "Hello, World!") -> str:
        def _rot13(s: str) -> str:
            s = ""
            for c in text:
                if 'a' <= c <= 'z':
                    s += chr((ord(c) - ord('a') + 13) % 26 + ord('a'))
                elif 'A' <= c <= 'Z':
                    s += chr((ord(c) - ord('A') + 13) % 26 + ord('A'))
                else:
                    s += c
            return s
        
        return _rot13(text)
```

## linting 

make sure your connectors pass the linting tests

```
~$ python3 scripts/syntac-lint.py ./connectors/demo.py

+ Imported class: Demo from ./connectors/demo.py
┌─ Connector: Demo
│  Globals Variables:
│    - None
│  Submodules:
│    - Python - Hello World:
│      - code: str (default: Hello, World!)
│    - Python - Add Numbers (Integers):
│      - a: int (default: 1)
│      - b: int (default: 1)
│    - Python - Add Numbers (Floats):
│      - a: float (default: 1.0)
│      - b: float (default: 1.0)
│    - rot13:
│      - text: str (default: Hello, World!)
└────────────────────────────────────────
```