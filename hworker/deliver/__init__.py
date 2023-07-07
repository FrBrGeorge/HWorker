"""Delivery interface"""
from abc import ABC


class Backend(ABC):
    def download_all(self):
        pass
