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

    def get_existing_inst_col_order(self):
        return ["Item","Document #", "Description","Signatories","Action","Circulation Notes","Status"]
    
    def get_new_agreements_col_order(self):
        return ["Item","Document/Desc", "Copies/Dept","Signatories","Condition of Approval","Circulation Notes","Status"]
    
    def get_document_tracking_statuses(self):
        return ["---","Prepared","Complete","No Action Required","Client for Execution","City for Execution","Third party for Execution"]

    def get_document_tracking_actions(self):
        return ["No Action Required","Consent","Partial Discharge","Full Discharge"]

    def get_instruments_on_title(self):
        return self.data.get_instruments_on_title()
    
    def get_loaded_insts_on_title(self):
        return self.data.get_loaded_insts_on_title()
    
    def load_instruments_on_title(self,filepath):
        reader = PdfReader(filepath)
        processed_title_cert = process_title_cert(reader)
        self.data.set_instruments_on_title(processed_title_cert["inst_on_title"])
        self.data.set_loaded_insts_on_title(processed_title_cert["inst_count_in_title"])

    def get_app_state(self):
        return self.data.get_app_state()
    
    def set_app_state(self,data):
        self.data.set_app_state(data)