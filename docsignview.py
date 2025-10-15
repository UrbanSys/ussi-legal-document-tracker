
class docsignview():
    def __init__(self):
        pass

    def determine_documents_to_sign(self,app_state):
        """
        ui_state = {
            "existing_encumbrances_on_title": [],
            "new_agreements": [],
            "plans": {}
        }
        """
        consent_documents_to_generate = {}
        partial_discharge_documents_to_generate = []
        full_discharge_documents_to_generate = []

        existing_enc_on_title = app_state["existing_encumbrances_on_title"]


        for doc in existing_enc_on_title:
            signatories = doc["Signatories"].lower()
            sign_split = signatories.split("\n")
            print(doc["Action"])
            if doc["Action"]=="Consent":
                for signer in sign_split:
                    if signer != '':
                        consent_doc = {
                            "company": signer,
                            "doc_number": doc["Document #"]
                        }
                        if signer not in consent_documents_to_generate:
                            consent_documents_to_generate[signer] = []
                        consent_documents_to_generate[signer].append(consent_doc)
            if doc["Action"]=="Partial Discharge":
                for signer in sign_split:
                    if signer != '':
                        partial_discharge_doc = {
                            "company": signer,
                            "doc_number": doc["Document #"]
                        }
                        partial_discharge_documents_to_generate.append(partial_discharge_doc)
            if doc["Action"]=="Full Discharge":
                for signer in sign_split:
                    if signer != '':
                        full_discharge_doc = {
                            "company": signer,
                            "doc_number": doc["Document #"]
                        }
                        full_discharge_documents_to_generate.append(full_discharge_doc)


        for key in consent_documents_to_generate:
            print("Consent document %s"%key)
            signer_docs = consent_documents_to_generate[key]
            for doc in signer_docs:
                print(doc["doc_number"])

        for item in partial_discharge_documents_to_generate:
            print("PD document %s - %s"%(item["company"],item["doc_number"]))

        for item in full_discharge_documents_to_generate:
            print("FD document %s - %s"%(item["company"],item["doc_number"]))