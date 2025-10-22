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
from templateGen import *

class DocTrackerActions():
    def __init__(self):
        self.data = DataStorage()
        # The following things below don't really matter to keep persistant (data.py is more so the persistant storage and basic app state)
        self.consent_documents_to_generate = {}
        self.partial_discharge_documents_to_generate = []
        self.full_discharge_documents_to_generate = []
        self.surveyor = "---"
        self.fileno = "0000.0000.00"
        self.legal_desc = ""
        self.plantype = ""

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

    def has_docs_to_generate(self):
        total_len = len(self.consent_documents_to_generate)+len(self.partial_discharge_documents_to_generate)+len(self.full_discharge_documents_to_generate)
        if total_len == 0:
            return True
        else:
            return False

    def get_consent_documents_to_generate(self):
        return self.consent_documents_to_generate

    def get_partial_discharge_documents_to_generate(self):
        return self.partial_discharge_documents_to_generate

    def get_full_discharge_documents_to_generate(self):
        return self.full_discharge_documents_to_generate

    def set_docs_to_sign(self):
        app_state = self.get_app_state()
        self.consent_documents_to_generate = {}
        self.partial_discharge_documents_to_generate = []
        self.full_discharge_documents_to_generate = []

        existing_enc_on_title = app_state["existing_encumbrances_on_title"]

        for doc in existing_enc_on_title:
            signatories = doc["Signatories"].lower()
            sign_split = signatories.split("\n")
            if doc["Action"]=="Consent":
                if doc["Status"]=="---":
                    for signer in sign_split:
                        if signer != '':
                            consent_doc = {
                                "company": signer,
                                "doc_number": doc["Document #"],
                                "desc": doc["Description"],
                                "consent_id": f"{doc['Document #']}|{doc['Description']}"
                            }
                            if signer not in self.consent_documents_to_generate:
                                self.consent_documents_to_generate[signer] = []
                            self.consent_documents_to_generate[signer].append(consent_doc)
            if doc["Action"]=="Partial Discharge":
                if doc["Status"]=="---":
                    for signer in sign_split:
                        if signer != '':
                            partial_discharge_doc = {
                                "company": signer,
                                "doc_number": doc["Document #"],
                                "desc": doc["Description"]
                            }
                            self.partial_discharge_documents_to_generate.append(partial_discharge_doc)
            if doc["Action"]=="Full Discharge":
                if doc["Status"]=="---":
                    for signer in sign_split:
                        if signer != '':
                            full_discharge_doc = {
                                "company": signer,
                                "doc_number": doc["Document #"],
                                "desc": doc["Description"]
                            }
                            self.full_discharge_documents_to_generate.append(full_discharge_doc)

    def set_surveyor(self, surveyor):
        self.surveyor = surveyor

    def set_fileno(self, fileno):
        self.fileno = fileno

    def set_legal_desc(self, legal_desc):
        self.legal_desc = legal_desc

    def set_plantype(self, plantype):
        self.plantype = plantype

    def set_survey_info(self, surveyor=None, fileno=None, legal_desc=None, plantype=None):
        if surveyor is not None:
            self.surveyor = surveyor
        if fileno is not None:
            self.fileno = fileno
        if legal_desc is not None:
            self.legal_desc = legal_desc
        if plantype is not None:
            self.plantype = plantype
    
    def do_templates(self, all_docs,prepared_callback=None):
        for doc in all_docs:
            file_path = doc["template_path"]
            signer = doc["signer"]
            docnumber = ""
            for item in doc["docs"]:
                docnumber = docnumber + item["doc_number"] + ", "
            output_filename = "%s %s - test.docx"%(signer,docnumber)
            if len(doc["docs"])>1:
                docnumber = docnumber[:-2]
                output_filename = "%s - test.docx"%(signer)
            generate_general_doc(file_path, output_filename, signer, "Subdivision", self.surveyor, self.fileno, self.legal_desc,docnumber)
            for item in doc["docs"]:   
                if prepared_callback:
                    prepared_callback.auto_set_prepared(item["doc_number"])