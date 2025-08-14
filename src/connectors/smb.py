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
        host: str = "",
        username: str = "",
        password: str = "",
        is_ntlm: bool = False,
        kerberos: bool = False,
    ) -> str:
        """
        Reference: [https://www.netexec.wiki/smb-protocol/authentication/checking-credentials-domain](https://www.netexec.wiki/smb-protocol/authentication/checking-credentials-domain)
        
        This submodule lists SMB shares using the [NetExec](https://github.com/Pennyw0rth/NetExec) tool.
        """
        if kerberos and is_ntlm:
            return f"nxc smb '{host}' -u '{username}' -H '{password}' --kerberos --shares"
        if kerberos:
            return f"nxc smb '{host}' --use-kcache --shares"
        if is_ntlm:
            return f"nxc smb '{host}' -u '{username}' -H '{password}' --shares"
        return f"nxc smb '{host}' -u '{username}' -p '{password}' --shares"

    @sub_module("List Shares (SMBClient)")
    def ls_smbclient(self, host: str = "", username: str = "", password:str = "") -> str:
        """
        Lists SMB shares using the [smbclient](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html) command-line tool.
        
        \* not to be mistaken with [smbclient.py](https://github.com/fortra/impacket/blob/master/examples/smbclient.py)
        """
        if not username and not password:
            return f"smbclient -L {host} -N"
        elif not password:
            return f"smbclient -L {host} -U {username}%"
        else:
            return f"smbclient -L {host} -U {username}%{password}"
