"""Mail utilities."""
from imap_tools import MailBox, MailboxFolderCreateError

__all__ = ["get_mailbox"]

from ...config import get_imap_info


def get_mailbox():
    """Get mailbox."""
    con_mailbox = MailBox(get_imap_info()["host"], get_imap_info()["port"])
    con_mailbox.login(get_imap_info()["username"], get_imap_info()["password"])
    try:
        con_mailbox.folder.create(get_imap_info()["folder"])
    except MailboxFolderCreateError:
        pass
    con_mailbox.folder.set(get_imap_info()["folder"])
    return con_mailbox
