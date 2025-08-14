# Syntac

a quick and dirty templating solution for creating cheatsheets quickly and easily

```bash
export FLASK_APP="app:init"
export FLASK_ENV=development
export FLASK_RUN_HOST='0.0.0.0'
flask run
```

[http://127.0.0.1:5000](http://127.0.0.1:5000) will be the default URL.

![](https://i.gyazo.com/e6ea25fb954f952cc598e59b850519ef.png)

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
        """
        Prints a given string in Python.
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
```

### documentation

docstrings are rendered as markdown, so you can use markdown syntax to format your documentation. for example, you can use links, code blocks, and lists.

```python
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
```

### optional arguments

anything top-level parameters will be considered a global variable and can be used in any submodule. for example, consider the following where `host`, `username` and `password` are globally accessible.

```python
@register_module
class Smb(Module):
    name = "SMB"
    description = "Enumerating and mapping the SMB protocol"

    host: str = ""
    username: str = ""
    password: str = ""
...
```

### submodule arguments

submodules may need additional arguments, for example for `kerberos` authentication. these are specified in the function signature of the submodule, where the `type` of the argument is respected.

```python

@register_module
class Smb(Module):
    name = "SMB"
    description = "Enumerating and mapping the SMB protocol"

    host: str = ""
    username: str = ""
    password: str = ""

    @sub_module("List Shares (NetExec)")
    def ls_nxc(
        self,
        is_ntlm: bool = False,
        kerberos: bool = False,
    ) -> str:
        """
        Reference: [https://www.netexec.wiki/smb-protocol/authentication/checking-credentials-domain](https://www.netexec.wiki/smb-protocol/authentication/checking-credentials-domain)
        
        This submodule lists SMB shares using the [NetExec](https://github.com/Pennyw0rth/NetExec) tool.
        """
        if kerberos and is_ntlm:
            return f"nxc smb '{self.host}' -u '{self.username}' -H '{self.password}' --kerberos --shares"
        if kerberos:
            return f"nxc smb '{self.host}' --use-kcache --shares"
        if is_ntlm:
            return f"nxc smb '{self.host}' -u '{self.username}' -H '{self.password}' --shares"
        return f"nxc smb '{self.host}' -u '{self.username}' -p '{self.password}' --shares"
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

## argparsing

you can use the `parser.py` script to hook into `argparse.ArgumentParser` of any program, and dump the arguments into a `submodule` capable signature.

note that this will almost always require some manual adjustments, as the generated signature will not be perfect. however, it should give you a good starting point.

```
~$ python3 parser.py /home/kali/.local/bin/rbcd.py
[--] Found 1 parsers in /home/kali/.local/bin/rbcd.py

def rbcd(
    identity: str = None,
    delegate_to: str = None,
    delegate_from: str = None,
    action: str = 'read',
    use_ldaps: bool = False,
    ts: bool = False,
    debug: bool = False,
    hashes: str = None,
    no_pass: bool = False,
    k: bool = False,
    aesKey: str = None,
    dc_ip: str = None,
    dc_host: str = None,
) -> str:
    """
    This is a rough estimate of what the script expects,
    note that this docstring should be omitted in the final code.

    Args:
        identity (str, optional): domain.local/username[:password]. Defaults to None.
        delegate_to (str, optional): Target account the DACL is to be read/edited/etc.. Defaults to None.
        delegate_from (str, optional): Attacker controlled account to write on the rbcd property of -delegate-to (only when using `-action write`). Defaults to None.
        action (str, optional): Action to operate on msDS-AllowedToActOnBehalfOfOtherIdentity. Defaults to read.
        use_ldaps (bool, optional): Use LDAPS instead of LDAP. Defaults to False.
        ts (bool, optional): Adds timestamp to every logging output. Defaults to False.
        debug (bool, optional): Turn DEBUG output ON. Defaults to False.
        hashes (str, optional): NTLM hashes, format is LMHASH:NTHASH. Defaults to None.
        no_pass (bool, optional): don't ask for password (useful for -k). Defaults to False.
        k (bool, optional): Use Kerberos authentication. Grabs credentials from ccache file (KRB5CCNAME) based on target parameters. If valid credentials cannot be found, it will use the ones specified in the command line. Defaults to False.
        aesKey (str, optional): AES key to use for Kerberos Authentication (128 or 256 bits). Defaults to None.
        dc_ip (str, optional): IP Address of the domain controller or KDC (Key Distribution Center) for Kerberos. If omitted it will use the domain part (FQDN) specified in the identity parameter. Defaults to None.
        dc_host (str, optional): Hostname of the domain controller or KDC (Key Distribution Center) for Kerberos. If omitted, -dc-ip will be used. Defaults to None.

    Returns:
        str: The resultant output of the submodule.
    """
    pass
```
