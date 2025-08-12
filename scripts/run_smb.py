#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is an example of how you could test your own connectors programmatically and healessly.
"""


import sys
import os
from typing import get_type_hints
import inspect
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connectors.smb import Smb as connector

if __name__ == "__main__":

    # This returns all of the parameters for the class, including the base class
    module_types = get_type_hints(connector)

    print(f"Parameters for {connector.__name__}:")
    print('\n'.join([
        f"  - {param}: {type_.__name__ if hasattr(type_, '__name__') else str(type_)}" 
        for param, type_ in module_types.items()
    ]))

    # We can grab all of the global parameters, and filter out the base class while getting the type hints
    relevant_global_params = {
        param: val 
        for param, val in connector().get_params().items() 
        if param not in [attr for attr, _ in inspect.getmembers(connector.__bases__[0]) if not attr.startswith('__')]
    }

    type_mapping = {
        param: type_.__name__ if hasattr(type_, '__name__') else str(type_)
        for param, type_ in module_types.items()
        if param in relevant_global_params
    }

    # With the grabbed parameters, we can now programmatically access them (or "refer" to them, like in the webapp!)
    print(f"\nGlobal parameters for {connector.__name__}:")
    print('\n'.join([
        f"  - {param}: {type_mapping[param]}"
        for param in relevant_global_params
    ]))

    # Now, some submodules have parameters that are not global. These are, obviously, not accessible from the parent class.
    print(f"\nSubmodules for {connector.__name__}:")
    submodules = connector().get_submodules()
    print('\n'.join([
        f"  - {submodule}: {connector.sub_modules[submodule].__name__}"
        for submodule in submodules
    ]))

    for submodule in submodules:
        sig = connector().get_submodule_params(submodule)
        print(f"\nParameters for submodule '{submodule}':")
        print('\n'.join([
            f"  - {param}: {type_.annotation.__name__ if hasattr(type_.annotation, '__name__') else str(type_.annotation)}"
            for param, type_ in sig.items()
        ]))

    # **If you don't care about programmatically accessing the parameters, you can just run a submodule directly
    
    ## host, username, and password are "global" parameters - which will be inherited from the submodules
    kwargs = {
        "is_ntlm": True,
    }

    print(
        connector(host="dc01.example.com", username="test",password="test")
            .run_sub_module(key="List Shares (NetExec)", **kwargs)
    )

    ## alternatively, you can override the global parameters in the submodules. this will not pollute the parent
    kwargs = {
        "host": "dc01.example.com",
        "username": "test",
        "password": "test",
    }

    print(
        connector(host="dc02.example.com", username="test2", password="test2")
            .run_sub_module(key="List Shares (NetExec)", **kwargs)
    )

    ## Since the `List Shares (NetExec)` submodule also exposes the `is_ntlm` and `kerberos` parameters
    kwargs = {
        "is_ntlm": False,
        "kerberos": True,
    }

    print(
        connector(host="dc03.example.com", username="test3", password="test3")
            .run_sub_module(key="List Shares (NetExec)", **kwargs)
    )

    ## Logical handling of the parameters is done in the submodule itself, consider the following:
    print("\n--- logic ---")

    ### If both ntlm and kerberos, then Kerberos authentication with NTLM is used.
    print(
        connector(host="dc04.example.com", username="test4", password="test4")
            .run_sub_module(key="List Shares (NetExec)", is_ntlm=True, kerberos=True)
    )

    ### If only kerberos, then KRB5CCNAME is used.
    print(
        connector(host="dc05.example.com", username="test5", password="test5")
            .run_sub_module(key="List Shares (NetExec)", kerberos=True, is_ntlm=False)
    )

    ### If only NTLM, then NTLM authentication is used.
    print(
        connector(host="dc06.example.com", username="test6", password="test6")
            .run_sub_module(key="List Shares (NetExec)", is_ntlm=True, kerberos=False)
    )







    
