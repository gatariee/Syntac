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
~$ python3 scripts/parser.py /opt/tools/krbrelayx/dnstool.py --doc-string
[--] Found 1 parsers in /opt/tools/krbrelayx/dnstool.py

def dnstool(
    host: str = None,
    user: str = None,
    password: str = None,
    forest: bool = False,
    legacy: bool = False,
    zone: str = None,
    print_zones: bool = False,
    print_zones_dn: bool = False,
    tcp: bool = False,
    kerberos: bool = False,
    port: str = 389,
    force_ssl: bool = False,
    dc_ip: str = None,
    dns_ip: str = None,
    aesKey: str = None,
    record: str = None,
    action: str = 'query',
    type: str = 'A',
    data: str = None,
    allow_multiple: bool = False,
    ttl: str = 180,
) -> str:
    """
    This is a rough estimate of what the script expects.

    Args:
        host (str, optional): Hostname/ip or ldap://host:port connection string to connect to. Defaults to None.
        user (str, optional): DOMAIN\username for authentication.. Defaults to None.
        password (str, optional): Password or LM:NTLM hash, will prompt if not specified. Defaults to None.
        forest (bool, optional): Search the ForestDnsZones instead of DomainDnsZones. Defaults to False.
        legacy (bool, optional): Search the System partition (legacy DNS storage). Defaults to False.
        zone (str, optional): Zone to search in (if different than the current domain). Defaults to None.
        print_zones (bool, optional): Only query all zones on the DNS server, no other modifications are made. Defaults to False.
        print_zones_dn (bool, optional): Query and print the Distinguished Names of all zones on the DNS server. Defaults to False.
        tcp (bool, optional): use DNS over TCP. Defaults to False.
        kerberos (bool, optional): Use Kerberos authentication. Grabs credentials from ccache file (KRB5CCNAME) based on target parameters. If valid credentials cannot be found, it will use the ones specified in the command line. Defaults to False.
        port (str, optional): LDAP port, default value is 389. Defaults to 389.
        force_ssl (bool, optional): Force SSL when connecting to LDAP server. Defaults to False.
        dc_ip (str, optional): IP Address of the domain controller. If omitted it will use the domain part (FQDN) specified in the target parameter. Defaults to None.
        dns_ip (str, optional): IP Address of a DNS Server. Defaults to None.
        aesKey (str, optional): AES key to use for Kerberos Authentication (128 or 256 bits). Defaults to None.
        record (str, optional): Record to target (FQDN). Defaults to None.
        action (str, optional): Action to perform. Options: add (add a new record), modify (modify an existing record), query (show existing), remove (mark record for cleanup from DNS cache), delete (delete from LDAP). Default: query. Defaults to query.
        type (str, optional): Record type to add (Currently only A records supported). Defaults to A.
        data (str, optional): Record data (IP address). Defaults to None.
        allow_multiple (bool, optional): Allow multiple A records for the same name. Defaults to False.
        ttl (str, optional): TTL for record (default: 180). Defaults to 180.

    Returns:
        str: The resultant output of the submodule.
    """
    # maps function param name to CLI option string
    __arg_map__ = {
        'host': '',
        'user': '-u',
        'password': '-p',
        'forest': '--forest',
        'legacy': '--legacy',
        'zone': '--zone',
        'print_zones': '--print-zones',
        'print_zones_dn': '--print-zones-dn',
        'tcp': '--tcp',
        'kerberos': '-k',
        'port': '-port',
        'force_ssl': '-force-ssl',
        'dc_ip': '-dc-ip',
        'dns_ip': '-dns-ip',
        'aesKey': '-aesKey',
        'record': '-r',
        'action': '-a',
        'type': '-t',
        'data': '-d',
        'allow_multiple': '--allow-multiple',
        'ttl': '--ttl',
    }
    # ...implementation goes here
    pass


```
