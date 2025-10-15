import tkinter as tk

class HandleActions():
    def __init__(self):
        self.consent_documents_to_generate = {}
        self.partial_discharge_documents_to_generate = []
        self.full_discharge_documents_to_generate = []

    def generate_documents_gui(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Existing Encumbrances")
        self.window.minsize(width=800,height=620)
        self.window.withdraw()
        self.window.protocol("WM_DELETE_WINDOW", self.window.withdraw)
        self.window.deiconify()

        canvas = tk.Canvas(self.window)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.row_index = 0
        
        self.write_header("Consent Docs")
        for key in self.consent_documents_to_generate:
            signer_docs = self.consent_documents_to_generate[key]
            docs_string = ""
            for doc in signer_docs:
                docs_string = docs_string + doc["doc_number"] + ", "
            self.write_line(key,docs_string)

        self.write_header("Partial Discharge Docs")   
        for item in self.partial_discharge_documents_to_generate:
            self.write_line(item["company"],item["doc_number"])

        self.write_header("Full Discharge Docs")
        for item in self.full_discharge_documents_to_generate:
            self.write_line(item["company"],item["doc_number"])

    def _on_mousewheel(self, event):
        # On Windows and Mac, event.delta is multiples of 120
        self.scrollable_frame.update_idletasks()  # Make sure layout updated
        self.scrollable_frame.master.yview_scroll(int(-1*(event.delta/120)), "units")

    def write_line(self, company, doc_nums):
        txt = tk.Label(self.scrollable_frame,text=company,anchor="w")
        txt.grid(row=self.row_index,column=0, sticky="w")
        txt2 = tk.Label(self.scrollable_frame,text=doc_nums,anchor="w")
        txt2.grid(row=self.row_index,column=1, sticky="w")
        chk = tk.Checkbutton(self.scrollable_frame)
        chk.grid(row=self.row_index,column=2)
        chk.select()
        self.row_index+=1

    def write_header(self, text):
        txt = tk.Label(self.scrollable_frame,text=text,font=("Arial", 10, "bold"))
        txt.grid(row=self.row_index,column=0)
        self.row_index+=1

    def is_view_empty(self):
        total_len = len(self.consent_documents_to_generate)+len(self.partial_discharge_documents_to_generate)+len(self.full_discharge_documents_to_generate)
        if total_len == 0:
            return True
        else:
            return False

    def determine_documents_to_sign(self,app_state):
        """
        ui_state = {
            "existing_encumbrances_on_title": [],
            "new_agreements": [],
            "plans": {}
        }
        """
        self.consent_documents_to_generate = {}
        self.partial_discharge_documents_to_generate = []
        self.full_discharge_documents_to_generate = []

        existing_enc_on_title = app_state["existing_encumbrances_on_title"]


        for doc in existing_enc_on_title:
            signatories = doc["Signatories"].lower()
            sign_split = signatories.split("\n")
            if doc["Action"]=="Consent":
                for signer in sign_split:
                    if signer != '':
                        consent_doc = {
                            "company": signer,
                            "doc_number": doc["Document #"]
                        }
                        if signer not in self.consent_documents_to_generate:
                            self.consent_documents_to_generate[signer] = []
                        self.consent_documents_to_generate[signer].append(consent_doc)
            if doc["Action"]=="Partial Discharge":
                for signer in sign_split:
                    if signer != '':
                        partial_discharge_doc = {
                            "company": signer,
                            "doc_number": doc["Document #"]
                        }
                        self.partial_discharge_documents_to_generate.append(partial_discharge_doc)
            if doc["Action"]=="Full Discharge":
                for signer in sign_split:
                    if signer != '':
                        full_discharge_doc = {
                            "company": signer,
                            "doc_number": doc["Document #"]
                        }
                        self.full_discharge_documents_to_generate.append(full_discharge_doc)