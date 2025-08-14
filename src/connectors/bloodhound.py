from .base import Module, register_module, sub_module


@register_module
class BloodHound(Module):
    name = "BloodHound"
    description = ""

    domain: str = ""
    username: str = ""
    password: str = ""
    kerberos: bool = False

    @sub_module("Collection (BloodHound.py)")
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
    def run_netexec(self) -> str:
        if self.kerberos:
            return f"nxc ldap '{self.domain}' -u '{self.username}' -k --bloodhound --collection All"
        return f"nxc ldap '{self.domain}' -u '{self.username}' -p '{self.password}' --bloodhound --collection All"

    @sub_module("Collection (SharpHound)")
    def run_sharphound(
        self,
        output: str = "",
    ) -> str:
        return f"SharpHound.exe --CollectionMethods All --ZipFileName {output}.zip"

    @sub_module("Collection (RustHound-CE-Linux)")
    def run_rusthoundce_linux(
        self,
        ldapfqdn: str = "",
        path: str = "/tmp/rusthound",
        DConly: bool = False,
        ldapip: str = "",
        ldaps: bool = False,
        custom_port: int = 3269,
        fqdn_resolver: bool = False,
        redirect_file: str = "",
    ) -> str:
        """
        Collects BloodHound-CE using [RustHoundCE](https://github.com/g0h4n/RustHound-CE) from Linux
        """
        if ldaps and ldapip:
            raise ValueError("Cannot use both ldapip (-i) and ldaps (--ldaps) options at the same time. Clear ldapip field or uncheck ldaps!")

        if self.kerberos:
            return f"rusthound-ce -d '{self.domain}' -f {ldapfqdn} -k -o {path} -z"

        if DConly:
            return f"rusthound-ce -c DCOnly -d {self.domain} -u '{self.username}' -p '{self.password}' -o {path} -z"

        if ldapip:
            return f"rusthound-ce -d {self.domain} -i {ldapip} -u '{self.username}' -p '{self.password}' -o {path} -z"

        if ldaps and custom_port:
            return f"rusthound-ce -d {self.domain} --ldaps -P {custom_port} -u '{self.username}' -p '{self.password}' -o {path} -z"

        if ldaps:
            return f"rusthound-ce -d {self.domain} --ldaps -u '{self.username}' -p '{self.password}' -o {path} -z"

        if fqdn_resolver:
            return f"rusthound-ce -d {self.domain} --ldaps -u '{self.username}' -p '{self.password}' -o {path} --fqdn-resolver -z"

        if redirect_file:
            return f"rusthound-ce -d {self.domain} --ldaps -u '{self.username}' -p '{self.password}' -o {path} -z > {redirect_file} 2>&1"

        return f"rusthound-ce -d {self.domain} -u '{self.username}' -p '{self.password}' -o {path} -z"

    @sub_module("Collection (RustHound-CE-Windows)")
    def rusthound_win(
        self, 
        ldapfqdn: str = "",
        gssapi_session: bool = False,
    ) -> str:    
        """
        Collects BloodHound-CE using [RustHoundCE](https://github.com/g0h4n/RustHound-CE) from Linux
        """
        if self.kerberos:
            return f"rusthound-ce -d {self.domain} -f {ldapfqdn} -k -z"
        
        if gssapi_session:
            return f"rusthound-ce.exe -d {self.domain} --ldapfqdn {ldapfqdn}"
        else:
            return f"rusthound-ce.exe -d {self.domain} -u {self.username}l -p {self.password} -o output -z"