"""
actions.py
Gavin Schultz 2025
Contains functions to call when actions are needed to be done (i.e. clicking a button on an UI). This is 
where I define the actual behaivours for what the UI does. This should be done in a way so that the UI can be 
interchanged as needed, and all that needs to be done is have the UI point to these functions to do everything.
"""
from data import DataStorage

class DocTrackerActions():
    def __init__(self):
        self.data = DataStorage()

    def get_instruments_on_title(self):
        return self.data.get_instruments_on_title()