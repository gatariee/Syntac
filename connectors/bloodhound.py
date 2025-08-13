from .base import Module, register_module, sub_module


@register_module
class BloodHound(Module):
    name = "BloodHound"
    description = ""

   
    domain: str = ""
    username: str = ""
    password: str = ""
    kerberos: bool = False

    @sub_module("Collection  (BloodHound.py)")
    def run_bloodhoundpy(
        self,
        domain: str = "",
        username: str = "",
        password: str = "",
        nameserver: str= "",
        kerberos: bool = False,
    ) -> str:
        if kerberos:
            return f"bloodhound-python -u '{username}' -d '{domain}' -k -c all -v -ns {nameserver}"
        return f"bloodhound-python -u '{username}' -p '{password}' -d '{domain}' -c all -v -ns {nameserver}"

    @sub_module("Collection (NetExec)")
    def run_netexec(
        self,
        domain: str = "",
        username: str = "",
        password: str = "",
        kerberos: bool = False,
    ) -> str:
        if kerberos:
            return f"nxc ldap '{domain}' -u '{username}' -k --bloodhound --collection All"
        return f"nxc ldap '{domain}' -u '{username}' -p '{password}' --bloodhound --collection All"
        

    @sub_module("Collection (SharpHound)")
    def run_sharphound(
        self,
        output: str = "",
    ):
        return f"SharpHound.exe --CollectionMethods All --ZipFileName {output}.zip"

