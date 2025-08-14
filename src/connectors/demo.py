from .base import Module, register_module, sub_module
import textwrap


def wrap_code(template: str, /, **ctx) -> str:
    dedented = textwrap.dedent(template).strip()
    return dedented.format(**ctx)


# Uncomment the following line to register the module
# @register_module
class Demo(Module):
    name = "Demo"
    description = ""

    @sub_module("Example Submodule")
    def example_submodule(self) -> str:
        """
        This is an example submodule.

        It demonstrates how to use **bold** text, *italic* text, and [links](https://example.com).

        ```python
        print("Hello, World!")
        ```
        
        You can also include lists:
        
        - Item 1
        - Item 2
        - Item 3
        """
        return "Example submodule executed."

    @sub_module("Python - Hello World")
    def py_hello_world(self, code: str = "Hello, World!") -> str:
        """
        Prints a given string in Python.
        ```
        print("hello world")
        ```
        """
        return wrap_code(
            f"""
            print("{code}")
            """
        )

    @sub_module("Python - Add Numbers (Integers)")
    def py_add_numbers(self, a: int = 1, b: int = 1) -> str:
        """
        Adds two integers in Python.
        """
        return int(a) + int(b)

    @sub_module("Python - Add Numbers (Floats)")
    def py_add_numbers_float(self, a: float = 1.0, b: float = 1.0) -> str:
        """
        Adds two floating-point numbers in Python.
        """
        return float(a) + float(b)

    @sub_module("rot13")
    def rot13(self, text: str = "Hello, World!") -> str:
        """
        Rotates the characters in a string by 13 positions in the alphabet.
        """
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