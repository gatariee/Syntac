from .base import Module, register_module, sub_module


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
        host,
        username="",
        password="",
        is_ntlm: bool = False,
        kerberos: bool = False,
    ) -> str:
        if kerberos:
            return f"nxc smb '{host}' --use-kcache"
        if is_ntlm:
            return f"nxc smb {host} -u '{username}' -H '{password}' --shares"
        return f"nxc smb '{host}' -u '{username}' -p '{password}' --shares"

    @sub_module("List Shares (SMBClient)")
    def ls_smbclient(self, host, username="", password="") -> str:
        if not username and not password:
            return f"smbclient -L {host} -N"
        elif not password:
            return f"smbclient -L {host} -U {username}%"
        else:
            return f"smbclient -L {host} -U {username}%{password}"
