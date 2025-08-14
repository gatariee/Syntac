#!/usr/bin/env python3

import argparse
import runpy
import sys
import os

from typing import List
from contextlib import redirect_stdout, redirect_stderr

from argparse import (
    _HelpAction,
    _StoreAction,
    _StoreTrueAction,
    _StoreFalseAction,
    _AppendAction,
    _CountAction,
    _VersionAction,
    _SubParsersAction,
    Action,
    ArgumentParser,
)
from dataclasses import dataclass
from typing import Any, List, Union


@dataclass
class _SyntacSig:
    type: str
    dest: str
    default: Any
    option_strings: Union[str, List[str]]
    help: str

    def __post_init__(self):
        if isinstance(self.option_strings, list):
            self.option_strings = self.option_strings[0] if self.option_strings else ""


_original_init = argparse.ArgumentParser.__init__
_registered_parsers: List[argparse.ArgumentParser] = []


def _recording_init(self, *args, **kwargs):
    _original_init(self, *args, **kwargs)
    _registered_parsers.append(self)


def itsp(sp: str) -> List[ArgumentParser]:

    # fix relative imports
    script_dir = os.path.dirname(os.path.abspath(sp))
    sys.path.insert(0, script_dir)

    # 1) hook argparse
    argparse.ArgumentParser.__init__ = _recording_init

    # 2) hijack sys.argv so the script doesn't error on missing args
    old_argv = sys.argv
    sys.argv = [sp]

    # 3) prepare a devnull to swallow stdout/stderr
    devnull = open(os.devnull, 'w')
    try:
        with redirect_stdout(devnull), redirect_stderr(devnull):
            try:
                runpy.run_path(sp, run_name="__main__")
            except SystemExit:
                pass
    finally:
        sys.argv = old_argv
        argparse.ArgumentParser.__init__ = _original_init
        devnull.close()

    # 4) introspect the "stolen" parsers
    print(f"[--] Found {len(_registered_parsers)} parsers in {sp}\n")
    return _registered_parsers


def _lex(action: Action) -> Union[_SyntacSig, None]:
    if isinstance(action, _HelpAction):
        return None

    base = dict(
        dest=action.dest,
        option_strings=action.option_strings,
        help=action.help or "",
    )

    if isinstance(action, _StoreAction):
        return _SyntacSig(
            type="str",
            default=action.default,
            **base
        )

    if isinstance(action, _StoreTrueAction):
        default = action.default if action.default is not None else False
        return _SyntacSig(
            type="bool",
            default=default,
            **base
        )

    if isinstance(action, _StoreFalseAction):
        default = action.default if action.default is not None else True
        return _SyntacSig(
            type="bool",
            default=default,
            **base
        )

    if isinstance(action, _AppendAction):
        default = action.default if action.default is not None else []
        return _SyntacSig(
            type="list[str]",
            default=default,
            **base
        )

    if isinstance(action, _CountAction):
        default = action.default if action.default is not None else 0
        return _SyntacSig(
            type="int",
            default=default,
            **base
        )

    if isinstance(action, _VersionAction):
        return _SyntacSig(
            type="version",
            default=None,
            **base
        )

    if isinstance(action, _SubParsersAction):
        subparsers = {
            cmd: list(parser._actions)
            for cmd, parser in action.choices.items()
        }
        return _SyntacSig(
            type="subparsers",
            default=subparsers,
            **base
        )

    return _SyntacSig(
        type=action.__class__.__name__,
        default=getattr(action, "default", None),
        **base
    )

def generate_signature(
    parser: ArgumentParser,
    docstring: bool = True,
) -> str:
    """
    Generate a stub function signature for the given ArgumentParser.

    If NO_DOCSTRING is True, only the function definition, parameters,
    and a pass statement are emitted (no docstring).

    Otherwise, a full docstring describing each parameter is included.
    """
    fn = parser.prog.replace(" ", "_").replace(".py", "")
    sigs: List[_SyntacSig] = []
    for action in parser._actions:
        sig = _lex(action)
        if sig is not None:
            sigs.append(sig)

    param_lines = [
        f"    {s.dest}: {s.type} = {repr(s.default)},"
        for s in sigs
    ]
    params_block = "\n".join(param_lines)

    if not docstring:
        return f"""\
def {fn}(
{params_block}
) -> str:
    pass
"""

    doc_params = "\n".join(
        f"        {s.dest} ({s.type}, optional): {s.help}. "
        f"Defaults to {s.default}."
        for s in sigs
    )

    return f"""\
def {fn}(
{params_block}
) -> str:
    \"\"\"
    This is a rough estimate of what the script expects,
    note that this docstring should be omitted in the final code.

    Args:
{doc_params}

    Returns:
        str: The resultant output of the submodule.
    \"\"\"
    pass
"""


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "script",
        help="Path to the Python script to introspect.",
        action="store",
    )

    parser.add_argument(
        "--doc-string",
        help="Generate a docstring for the function signature.",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()
    
    if not args.script:
        parser.print_usage()
        sys.exit(1)

    parsers = itsp(sys.argv[1])
    for parser in parsers:
        print(generate_signature(
            parser=parser,
            docstring=args.doc_string
        ))