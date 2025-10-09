"""
data.py
Gavin Schultz 2025
Stores currently loaded data in this session. Eventually will support persistance.
Contains getters so that steps can be performed before data is retrieved, if needed
"""

class DataStorage():
    def __init__(self):
        self.instruments_on_title = []

    def get_instruments_on_title(self):
        return self.instruments_on_title
    