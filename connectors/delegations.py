from .base import Module, register_module, sub_module


@register_module
class Delegations(Module):
    name = "Delegations"
    description = ""

    dc_host: str = ""
    domain: str = ""
    username: str = ""
    password: str = ""
    is_ntlm: bool = False

    @sub_module("Find Delegations (NetExec)")
    def find_delegations_nxc(
        self,
        dc_host: str = "",
        username: str = "",
        password: str = "",
        is_ntlm: bool = False,
    ) -> str:
        if is_ntlm:
            return (
                f"nxc ldap {dc_host} -u '{username}' -H '{password}' --find-delegation"
            )
        return f"nxc ldap {dc_host} -u '{username}' -p '{password}' --find-delegation"

    @sub_module("Find Delegations (findDelegation.py)")
    def find_delegations_impacket(
        self,
        domain: str = "",
        username: str = "",
        password: str = "",
        is_ntlm: bool = False,
    ) -> str:
        if is_ntlm:
            return f"findDelegation.py '{domain}'/'{username}' -hashes ':{password}'"
        return f"findDelegation.py '{domain}'/'{username}':'{password}'"
