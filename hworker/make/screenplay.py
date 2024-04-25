#!/usr/bin/env python3
'''
Utility functions for screenplay screen dump.

Uses GNU screen got now.
'''

import re
from pathlib import Path
from tempfile import TemporaryDirectory as tmpdir
from ..log import get_logger
from subprocess import run

# report.01.second/./BOTH.txt
REname = re.compile(r'report....(\w+)[./]+(\w+)[.]txt')
log = get_logger(__name__)


def screendump(command: str, directory: Path) -> bytes:
    """Run a shell command and dump result's screen buffer."""
    S = directory / "SCREEN"
    res = run(["screen", "-Dm", "/bin/bash", "-c", f"{command}; screen -X hardcopy -h {S}"])
    if res.returncode:
        return f"!{res.returncode}".encode()
    else:
        return S.read_bytes()


def screenplay(both: bytes, timer: bytes) -> bytes:
    """Run scritreplayon bith / timer data and dump result's screen buffer."""
    with tmpdir() as Dname:
        D = Path(Dname)
        B, T = D / "BOTH.txt", D / "TIME.txt"
        B.write_bytes(both)
        T.write_bytes(timer)
        return screendump(f"scriptreplay -m 0.001 -t {T} -B {B}", D)


def screenplay_all(content: dict[bytes, bytes]) -> dict[bytes, bytes]:
    """Read report files, select every BOTH/TIME pair, play and dump them."""
    records = {tuple(REname.match(name).groups()): value for name, value in content.items()}
    hosts, dumps = {host for host, path in records}, {}
    for host in hosts:
        if (host, "BOTH") in records and (host, "TIME") in records:
            dumps[host] = screenplay(records[(host, "BOTH")], records[(host, "TIME")])
        else:
            log.warning(f"Incomplete {host} report")
    return dumps
