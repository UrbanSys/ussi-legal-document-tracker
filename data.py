"""
data.py
Gavin Schultz 2025
Stores currently loaded data in this session. Eventually will support persistance.
Contains getters so that steps can be performed before data is retrieved, if needed
"""

class DataStorage():
    def __init__(self):
        self.instruments_on_title = []
        self.instrument_count_on_title = 0
        self.app_state = {}

    def get_instruments_on_title(self):
        return self.instruments_on_title
    
    def set_instruments_on_title(self,array):
        self.instruments_on_title = array
    
    def get_loaded_insts_on_title(self):
        return self.instrument_count_on_title
    
    def set_loaded_insts_on_title(self,val):
        self.instrument_count_on_title = val

    def get_app_state(self):
        return self.app_state
    
    def set_app_state(self,data):
        self.app_state = data