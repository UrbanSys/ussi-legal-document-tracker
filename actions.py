"""
actions.py
Gavin Schultz 2025
Contains functions to call when actions are needed to be done (i.e. clicking a button on an UI). This is 
where I define the actual behaivours for what the UI does. This should be done in a way so that the UI can be 
interchanged as needed, and all that needs to be done is have the UI point to these functions to do everything.
"""
from data import DataStorage
from utils import *
from pypdf import PdfReader

class DocTrackerActions():
    def __init__(self):
        self.data = DataStorage()
        self.insts_loaded = -1

    def get_instruments_on_title(self):
        return self.data.get_instruments_on_title()
    
    def get_loaded_insts_on_title(self):
        return self.insts_loaded
    
    def load_instruments_on_title(self,filepath):
        reader = PdfReader(filepath)
        processed_title_cert = process_title_cert(reader)
        self.data.set_instruments_on_title(processed_title_cert["inst_on_title"])
        self.insts_loaded = processed_title_cert["inst_count_in_title"]