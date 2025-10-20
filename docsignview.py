import os
import tkinter as tk
from tkinter import ttk
from utils import *
from tkinter import messagebox as mb

DEFAULT_CONFIG = "Z:/Urban Survey/Calgary/Automation/discharge_consent_config.txt"

class HandleActions():
    def __init__(self,app=None,main_gui_callback = None):
        (self.full_discharges_templates,self.partial_discharges_templates,self.consents_templates) = load_config(DEFAULT_CONFIG)
        self.app = app
        self.window = None
        self.main_gui_callback = main_gui_callback
        self.consent_doc_decisions = []
        self.partial_doc_decisions = []
        self.full_doc_decisions = []
        self.choice_lookup = {}

    def generate_documents_gui(self, root):
        if self.window:
            self.window.withdraw()
        self.window = tk.Toplevel(root)
        self.window.title("Existing Encumbrances")
        self.window.minsize(width=1400,height=620)
        self.window.withdraw()
        self.window.protocol("WM_DELETE_WINDOW", self.window.withdraw)
        self.window.deiconify()

        (self.full_discharges_templates,self.partial_discharges_templates,self.consents_templates) = load_config(DEFAULT_CONFIG)

        main_view = tk.Frame(self.window)
        main_view.pack(side="top",fill="both", expand=True)
        bottom_view = tk.Frame(self.window)
        bottom_view.pack(side="bottom")

        canvas = tk.Canvas(main_view)
        scrollbar = tk.Scrollbar(main_view, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.row_index = 0

        consent_documents_to_generate = self.app.get_consent_documents_to_generate()
        partial_discharge_documents_to_generate  = self.app.get_partial_discharge_documents_to_generate()
        full_discharge_documents_to_generate  = self.app.get_full_discharge_documents_to_generate()

        self.consent_doc_decisions = []
        self.partial_doc_decisions = []
        self.full_doc_decisions = []
        self.choice_lookup = {}
        
        self.write_header("Consent Docs")
        for key in consent_documents_to_generate:
            signer_docs = consent_documents_to_generate[key]
            self.write_line(key,signer_docs,self.consent_doc_decisions,self.full_discharges_templates)

        self.write_header("Partial Discharge Docs")   
        for item in partial_discharge_documents_to_generate:
            doc_array = [{"doc_number": item["doc_number"]}]
            self.write_line(item["company"],doc_array, self.partial_doc_decisions,self.partial_discharges_templates)

        self.write_header("Full Discharge Docs")
        for item in full_discharge_documents_to_generate:
            doc_array = [{"doc_number": item["doc_number"]}]
            self.write_line(item["company"],doc_array, self.full_doc_decisions,self.consents_templates)

        self._bind_mousewheel_to_widgets(self.scrollable_frame)

        button = tk.Button(bottom_view,text="Generate Templates",command=self.do_templates)
        button.grid(row=0, column=0)

    def _bind_mousewheel_to_widgets(self, widget):
        widget.bind("<Enter>", lambda e: widget.bind_all("<MouseWheel>", self._on_mousewheel))
        widget.bind("<Leave>", lambda e: widget.unbind_all("<MouseWheel>"))
        if isinstance(widget, (tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Canvas)):
            for child in widget.winfo_children():
                self._bind_mousewheel_to_widgets(child)

    def _on_mousewheel(self, event):
        try:
            widget = self.window.focus_get()
            # Skip scrolling if the focused widget is a Combobox
            if isinstance(widget, ttk.Combobox):
                return
        except Exception as e:
            # If the widget can't be resolved (e.g., 'popdown'), just ignore the scroll
            return

        # Otherwise, scroll the canvas
        self.scrollable_frame.master.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _dont_scroll(self,event):
        self._on_mousewheel(event)
        return "break"

    def write_line(self, company, doc_array, doc_list,options=None):
        txt = tk.Label(self.scrollable_frame,text=company,anchor="w")
        txt.grid(row=self.row_index,column=0, sticky="w")
        docs_string = ""
        for doc in doc_array:
            docs_string = docs_string + doc["doc_number"] + ", "
        txt2 = tk.Label(self.scrollable_frame,text=docs_string,anchor="w")
        txt2.grid(row=self.row_index,column=1, sticky="w")

        combo_var = tk.StringVar(value="")  # Default is blank
        combobox = ttk.Combobox(self.scrollable_frame, textvariable=combo_var, state="readonly",width=90)
        if options:
            combobox['values'] = [""] + self.generate_gui_template_chooser(options)
        combobox.grid(row=self.row_index, column=2, sticky="we")
        doc_data = {}
        doc_data["selection"] = combo_var
        doc_data["docs"] = doc_array
        doc_list.append(doc_data)
        combobox.bind("<MouseWheel>", self._dont_scroll)
        self.row_index+=1

    def generate_gui_template_chooser(self, gui_choice):
        grouped = {}
        for item in gui_choice:
            muni = item["municipality"]
            file_name = item["path"]
            grouped.setdefault(muni, []).append(file_name)

        self.selected_file = tk.StringVar()
        self.selected_file.set(None)

        ret_array = []

        for municipality, paths in grouped.items():
            #municipality

            for path in paths:
                file_name = os.path.basename(path)
                option_txt = municipality+" | "+file_name
                ret_array.append(option_txt)
                self.choice_lookup[option_txt] = path
        
        return ret_array

    def write_header(self, text):
        txt = tk.Label(self.scrollable_frame,text=text,font=("Arial", 10, "bold"))
        txt.grid(row=self.row_index,column=0)
        self.row_index+=1

    def is_view_empty(self):
        return self.app.has_docs_to_generate()

    def determine_documents_to_sign(self):
        self.app.set_docs_to_sign()

    def do_templates(self):
        doc_to_generate = []

        for item in self.consent_doc_decisions:
            self.gen_doc_dict(item,doc_to_generate)

        for item in self.partial_doc_decisions:
            self.gen_doc_dict(item,doc_to_generate)

        for item in self.full_doc_decisions:
            self.gen_doc_dict(item,doc_to_generate)

        if self.main_gui_callback:
            self.app.do_templates(doc_to_generate,self.main_gui_callback)
            self.main_gui_callback.auto_set_no_action_required()
            mb.showinfo("message","message")

    def gen_doc_dict(self,item,list):
        choice = item["selection"].get()
        if choice in self.choice_lookup:
            path = self.choice_lookup[choice]
            doc_dict = {}
            doc_dict["template_path"] = path
            doc_dict["docs"] = item["docs"]
            list.append(doc_dict)
            #ADD THINGS TO INCLUDE IN TEMPLATE