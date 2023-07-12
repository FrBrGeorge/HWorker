"""Mail utilities."""
from imap_tools import MailBox, MailboxFolderCreateError

__all__ = ["get_mailbox"]

from .config import load_configs


def get_mailbox():
    """Get mailbox."""
    configs = load_configs()
    con_mailbox = MailBox(configs["IMAP"]["email server host"], configs["IMAP"]["email server port"])
    con_mailbox.login(configs["IMAP"]["Username"], configs["IMAP"]["Password"])
    try:
        con_mailbox.folder.create(configs["IMAP"]["folder"])
    except MailboxFolderCreateError:
        pass
    con_mailbox.folder.set(configs["IMAP"]["folder"])
    return con_mailbox
