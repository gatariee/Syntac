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
    ) -> str:
        if self.is_ntlm:
            return (
                f"nxc ldap {self.dc_host} -u '{self.username}' -H '{self.password}' --find-delegation"
            )
        return f"nxc ldap {self.dc_host} -u '{self.username}' -p '{self.password}' --find-delegation"

    @sub_module("Find Delegations (findDelegation.py)")
    def find_delegations_impacket(
        self,
    ) -> str:
        if self.is_ntlm:
            return f"findDelegation.py '{self.domain}'/'{self.username}' -hashes ':{self.password}'"
        return f"findDelegation.py '{self.domain}'/'{self.username}':'{self.password}'"
