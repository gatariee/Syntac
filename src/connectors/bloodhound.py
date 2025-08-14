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
        nameserver: str = "",
        verbose: bool = False,
    ) -> str:
        """
        Collects BloodHound (Legacy) data using [bloodhound-python](https://github.com/dirkjanm/BloodHound.py)
        """
        cmd = ""
        if self.kerberos:
            cmd += f"bloodhound-python -u '{self.username}' -d '{self.domain}' -k -c all"
        else:
            cmd += f"bloodhound-python -u '{self.username}' -p '{self.password}' -d '{self.domain}' -c all"
        
        if nameserver:
            cmd += f" -ns {nameserver}"

        if verbose:
            cmd += " -v"
        
        return cmd

    @sub_module("Collection (NetExec)")
    def run_netexec(
        self,
    ) -> str:
        if self.kerberos:
            return f"nxc ldap '{self.domain}' -u '{self.username}' -k --bloodhound --collection All"
        return f"nxc ldap '{self.domain}' -u '{self.username}' -p '{self.password}' --bloodhound --collection All"
        

    @sub_module("Collection (SharpHound)")
    def run_sharphound(
        self,
        output: str = "",
    ):
        return f"SharpHound.exe --CollectionMethods All --ZipFileName {output}.zip"

