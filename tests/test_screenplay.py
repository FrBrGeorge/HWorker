#!/usr/bin/env python3
'''
Scriptreplay
'''
import pytest
from hworker.make.screenplay import screenplay, screendump, screenplay_all
from pathlib import Path


@pytest.fixture()
def simplescript():
    """Simple typescript BOTH / TIME pair"""
    D = Path(__file__).parent
    R = b'[george@gear ~]$ echo "QQ"\nQQ\n[george@gear ~]$\nexit'
    return (D / "B.txt").read_bytes(), (D / "T.txt").read_bytes(), R


@pytest.fixture()
def escapescript():
    """Escape-avare typescript BOTH / TIME pair"""
    D = Path(__file__).parent
    R = b"[george@gear ~]$ echo -e '\\e[36;45;1mQQ'\nQQ\n[george@gear ~]$\nexit"
    return (D / "Besc.txt").read_bytes(), (D / "Tesc.txt").read_bytes(), R


@pytest.fixture()
def solution(simplescript, escapescript):
    # report.01.second/./BOTH.txt
    return {
        "report.01.simple/./BOTH.txt": simplescript[0],
        "report.01.simple/./TIME.txt": simplescript[1],
        "report.01.simple/./OUT.txt": b'',
        "report.01.escape/./BOTH.txt": escapescript[0],
        "report.01.escape/./TIME.txt": escapescript[1],
        "report.01.escape/./OUT.txt": b'',
    }


class TestScreenplay:
    """Base functions"""

    def test_screendump(self, tmp_path):
        """screendump echo"""
        assert screendump("echo QQ", tmp_path).strip() == b"QQ"

    def test_screendump_esc(self, tmp_path):
        """screendump with color"""
        assert screendump(r"echo -e '\e[36;45;1mQQ'", tmp_path).strip() == b"QQ"

    def test_screenplay(self, simplescript):
        """ screenplay echo"""
        assert screenplay(simplescript[0], simplescript[1]).strip() == simplescript[2]

    def test_screenplay_esc(self, escapescript):
        """screenplay with color"""
        assert screenplay(escapescript[0], escapescript[1]).strip() == escapescript[2]

    def test_screenplay_all(self, solution, simplescript, escapescript):
        """untarred solution"""
        res = {key: value.strip() for key, value in screenplay_all(solution).items()}
        assert res == {"simple": simplescript[2], "escape": escapescript[2]}
