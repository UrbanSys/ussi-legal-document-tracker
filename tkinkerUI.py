"""
tkinkerUI.py
Gavin Schultz 2025
A prototype of the UI in tkinker
"""
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from actions import DocTrackerActions
from docsignview import HandleActions
from tkinter import filedialog as fd

try:
    import genVersionNumber
    genVersionNumber.gen_version_info()
    from version_info import __VERSION_TEXT__
except ImportError:
    __VERSION_TEXT__ = "***version info unavalible***"

__FILE_VERSION__ = 1
__FILE_MIN_VERSION__ = 1
__PROGRAM_NAME__ = "USSI DOCUMENT TRACKER PROTOTYPE 2"

class tkinterUI(tk.Tk):
    def __init__(self):
        super().__init__()

        main_view = tk.Frame(self)
        main_view.pack(side="top",fill="both", expand=True)
        bottom_view = tk.Frame(self)
        bottom_view.pack(side="bottom")

        build_text = __VERSION_TEXT__
        self.title("%s - %s"%(__PROGRAM_NAME__,build_text))
        self.geometry("1000x600")

        self.app = DocTrackerActions()
        self.docview = HandleActions(self.app,self)

        #Main view
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

        #Insts on title
        self.ui_insts_on_title_header = []
        self.ui_insts_on_title = []
        self.ui_insts_on_title_label = tk.Label(self.scrollable_frame,text="EXISTING ENCUMBRANCES ON TITLE", font=("Arial", 10, "bold"))

        row_labels = self.app.get_existing_inst_col_order()
        for col in row_labels:
            txt = tk.Label(self.scrollable_frame,text=col)
            self.ui_insts_on_title_header.append(txt)

        for i in range(0,10):
            self.add_row_ex_enc()

        #New Agreements
        self.ui_new_agreements_header = []
        self.ui_new_agreements = []
        self.ui_new_agreements_label = tk.Label(self.scrollable_frame,text="NEW AGREEMENTS CONCURRENT WITH REGISTRATION", font=("Arial", 10, "bold"))

        row_labels = self.app.get_new_agreements_col_order()

        for col in row_labels:
            txt = tk.Label(self.scrollable_frame,text=col)
            self.ui_new_agreements_header.append(txt)

        for i in range(0,10):
            self.add_row_new_agreement()

        #Plans
        self.ui_new_plans_header = {}
        self.ui_new_plans = {}
        self.ui_new_plans_label = {}

        self.add_new_plan("SUB1")
        self.add_new_plan("URW1")
        self.add_new_plan("ODRW1")

        #Bottom bar
        button = tk.Button(bottom_view,text="Import Title",command=self.load_instruments_on_title)
        button.grid(row=0, column=0)
        button = tk.Button(bottom_view,text="Save",command=self.save_tracker)
        button.grid(row=0, column=1)
        button = tk.Button(bottom_view,text="Load",command=self.load_tracker)
        button.grid(row=0, column=2)
        button = tk.Button(bottom_view,text="Generate Documents from Templates",command=self.gen_docs)
        button.grid(row=0, column=3)
        button = tk.Button(bottom_view,text="Button",command=self.dummy)
        button.grid(row=0, column=4)

        self.regrid_rows()

    def _on_mousewheel(self, event):
        # On Windows and Mac, event.delta is multiples of 120
        self.scrollable_frame.update_idletasks()  # Make sure layout updated
        self.scrollable_frame.master.yview_scroll(int(-1*(event.delta/120)), "units")

    def _dont_scroll(self,event):
        self._on_mousewheel(event)
        return "break"
    
    def _bind_mousewheel_to_widgets(self, widget):
        widget.bind("<Enter>", lambda e: widget.bind_all("<MouseWheel>", self._on_mousewheel))
        widget.bind("<Leave>", lambda e: widget.unbind_all("<MouseWheel>"))
        if isinstance(widget, (tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Canvas)):
            for child in widget.winfo_children():
                self._bind_mousewheel_to_widgets(child)

    
    def format_rows(self):
        for row_widgets in self.ui_insts_on_title:
            for j, col in enumerate(self.app.get_existing_inst_col_order(),start=1):
                if col in row_widgets:
                    if row_widgets[col].winfo_class()=="Entry":
                        status = row_widgets["Status_Val"].get()
                        if status=="Prepared":
                            row_widgets[col].config(bg="lightgreen")
                        elif status=="Complete" or status=="No Action Required":
                            row_widgets[col].config(bg="gray")
                        elif status=="Client for Execution":
                            row_widgets[col].config(bg="#fff1c9")
                        else:
                            row_widgets[col].config(bg="white")
        for row_widgets in self.ui_new_agreements:
            for j, col in enumerate(self.app.get_existing_inst_col_order(),start=1):
                if col in row_widgets:
                    if row_widgets[col].winfo_class()=="Entry":
                        status = row_widgets["Status_Val"].get()
                        if status=="Prepared":
                            row_widgets[col].config(bg="lightgreen")
                        elif status=="Complete" or status=="No Action Required":
                            row_widgets[col].config(bg="gray")
                        elif status=="Client for Execution":
                            row_widgets[col].config(bg="#fff1c9")
                        else:
                            row_widgets[col].config(bg="white")

        for plan_key in self.ui_new_plans:
            for row_widgets in self.ui_new_plans[plan_key]:
                for j, col in enumerate(self.app.get_new_agreements_col_order(),start=1):
                    if col in row_widgets:
                        if row_widgets[col].winfo_class()=="Entry":
                            status = row_widgets["Status_Val"].get()
                            if status=="Prepared":
                                row_widgets[col].config(bg="lightgreen")
                            elif status=="Complete" or status=="No Action Required":
                                row_widgets[col].config(bg="gray")
                            elif status=="Client for Execution":
                                row_widgets[col].config(bg="#fff1c9")
                            else:
                                row_widgets[col].config(bg="white")

    def regrid_rows(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.grid_forget()

        rid = 0
        self.ui_insts_on_title_label.grid(row=rid, column=0, columnspan=5, sticky="w")
        rid+=1
        for i, col_widgets in enumerate(self.ui_insts_on_title_header, start=1):
            col_widgets.grid(row=rid, column=i)
        rid+=1
        for row_widgets in self.ui_insts_on_title:
            for j, col in enumerate(self.app.get_existing_inst_col_order(),start=1):
                if col in row_widgets:
                    row_widgets[col].grid(row=rid, column=j)
            rid  +=1

        for plan_key in self.ui_new_plans:
            self.ui_new_plans_label[plan_key].grid(row=rid, column=0, columnspan=5, sticky="w")
            rid+=1
            for i, col_widgets in enumerate(self.ui_new_plans_header[plan_key], start=1):
                col_widgets.grid(row=rid, column=i)
            rid+=1
            for row_widgets in self.ui_new_plans[plan_key]:
                for j, col in enumerate(self.app.get_new_agreements_col_order(),start=1):
                    if col in row_widgets:
                        row_widgets[col].grid(row=rid, column=j)
                rid  +=1

        self.ui_new_agreements_label.grid(row=rid, column=0, columnspan=5, sticky="w")
        rid+=1
        for i, col_widgets in enumerate(self.ui_new_agreements_header, start=1):
            col_widgets.grid(row=rid, column=i)
        rid+=1
        for row_widgets in self.ui_new_agreements:
            for j, col in enumerate(self.app.get_new_agreements_col_order(),start=1):
                if col in row_widgets:
                    row_widgets[col].grid(row=rid, column=j)
            rid  +=1
        self.app.set_app_state(self.get_ui_state())

        self.format_rows()
        self._bind_mousewheel_to_widgets(self.scrollable_frame)

    def auto_set_no_action_required(self):
        for row_widgets in self.ui_insts_on_title:
            for j, col in enumerate(self.app.get_existing_inst_col_order(),start=1):
                if col in row_widgets:
                    status = row_widgets["Action_Val"].get()
                    if status == "No Action Required":
                        status = row_widgets["Status_Val"].set("No Action Required")
        self.regrid_rows()


    def dummy(self):
        mb.showinfo("message","message")

    def gen_docs(self):
        self.app.set_app_state(self.get_ui_state())
        self.docview.determine_documents_to_sign()
        if not self.docview.is_view_empty():
            self.docview.generate_documents_gui(self)
        else:
            mb.showerror("No actions set!", "No actions are currently set. Please choose actions in order to generate legal documents.")

    def load_instruments_on_title(self):
        filepath = fd.askopenfilename(
            title="Open File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filepath:
            self.app.load_instruments_on_title(filepath)
            for row in self.ui_insts_on_title:
                for widget in row.values():
                    if hasattr(widget, "destroy"):
                        widget.destroy()
            self.ui_insts_on_title = []
            insts_on_title = self.app.get_instruments_on_title()
            row_labels = self.app.get_existing_inst_col_order()
            for i, inst in enumerate(insts_on_title,start=1):
                self.add_row_ex_enc(inst["reg_number"],inst["name"],inst["signatories"])
            
            self.regrid_rows()
            mb.showinfo("Successfully imported title!","Imported %i of %i instruments"%(len(insts_on_title),self.app.get_loaded_insts_on_title()))

    def load_tracker(self):
        file_path = fd.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Open JSON File"
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
            except Exception as e:
                mb.showerror("Unable to open file", f"There was an error reading the file {file_path}.\nError: {e}")
                return
            
            try:
                header = data["header"]
                file_version = header["file_version"]
                program_name = header["program_name"]
                program_version = header["program_version"]
                if program_name==__PROGRAM_NAME__:
                    if file_version >= __FILE_MIN_VERSION__ and file_version <= __FILE_VERSION__:
                        print("Version of program from file: %s"%program_version)
                    else:
                        mb.showerror("Unable to open file", f"There was an error reading the file {file_path}.\nInvalid version number! File is {file_version}, should be between {__FILE_MIN_VERSION__}, {__FILE_VERSION__}\nPlease track down a compatible version of this program, such as \n{program_version}")
                        return
                else: 
                    mb.showerror("Unable to open file", f"There was an error reading the file {file_path}.\nInvalid header: Not a USSI Document Tracker file!")
                    return
            except KeyError as e:
                mb.showerror("Unable to open file", f"There was an error reading the file {file_path}.\nInvalid file: Not a USSI Document Tracker file!")
                return

            self.app.set_app_state(data)
            self.load_ui_state(self.app.get_app_state())
            self.regrid_rows()
            mb.showinfo("Successfully imported title!","Load Successful")

    def save_tracker(self):
        file_path = fd.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save JSON File"
        )

        if file_path:
            self.app.set_app_state(self.get_ui_state())
            with open(file_path, 'w') as f:
                json.dump(self.app.get_app_state(), f, indent=4)
            print(f"Data saved to {file_path}")

    def add_new_plan(self,plan_name):
        """
        return ["Item","Document/Desc", "Copies/Dept","Signatories","Condition of Approval","Circulation Notes","Status"]
        """
        row_labels = self.app.get_new_agreements_col_order()
        plan_docs = []
        plan_docs_headers = []
        for col in row_labels:
            txt = tk.Label(self.scrollable_frame,text=col)
            plan_docs_headers.append(txt)

        self.ui_new_plans_label[plan_name] = tk.Label(self.scrollable_frame,text="PLAN - %s"%plan_name, font=("Arial", 10, "bold"))

        self.add_row_plan(plan_docs,"Surveyor's Affidavit")
        self.add_row_plan(plan_docs,"Consent")
        self.add_row_plan(plan_docs)

        self.ui_new_plans[plan_name] = plan_docs
        self.ui_new_plans_header[plan_name] = plan_docs_headers


    def add_row_plan(self,plan,doc_desc=""):
        """
        return ["Item","Document/Desc", "Copies/Dept","Signatories","Condition of Approval","Circulation Notes","Status"]
        """
        row = {}
        row["Item"]=tk.Label(self.scrollable_frame,text="%i"%(len(plan)+1))
        row["Document/Desc"]=tk.Entry(self.scrollable_frame,width=25)
        row["Document/Desc"].insert(0, doc_desc)
        row["Copies/Dept"]=tk.Entry(self.scrollable_frame,width=25)
        row["Signatories"]=tk.Entry(self.scrollable_frame,width=25)
        row["Condition of Approval"]=tk.Entry(self.scrollable_frame,width=25)
        #row["Signatories"].insert(0, signatories)
        row["Circulation Notes"]=tk.Entry(self.scrollable_frame,width=25)
        self.generate_dropdown("Status",self.app.get_document_tracking_statuses(),row)
        
        plan.append(row)

    def add_row_ex_enc(self,reg_number="",reg_name="",signatories=""):
        """
        new_inst["date"] = inst_date
        new_inst["reg_number"] = inst_rn
        new_inst["name"] = inst_name
        new_inst["description"] = inst_text
        new_inst["signatories"] = sign_text
        new_inst["temp_selection"] = 4
        """
        row = {}
        row["Item"]=tk.Label(self.scrollable_frame,text="%i"%(len(self.ui_insts_on_title)+1))
        row["Document #"]=tk.Entry(self.scrollable_frame,width=25)
        row["Document #"].insert(0, reg_number)
        row["Description"]=tk.Entry(self.scrollable_frame,width=25)
        row["Description"].insert(0, reg_name)
        row["Signatories"]=tk.Entry(self.scrollable_frame,width=25)
        row["Signatories"].insert(0, signatories)
        row["Circulation Notes"]=tk.Entry(self.scrollable_frame,width=25)
        self.generate_dropdown("Action",self.app.get_document_tracking_actions(),row)
        self.generate_dropdown("Status",self.app.get_document_tracking_statuses(),row)
        
        self.ui_insts_on_title.append(row)

    def add_row_new_agreement(self):
        """
        return ["Item","Document/Desc", "Copies/Dept","Signatories","Condition of Approval","Circulation Notes","Status"]
        """
        row = {}
        row["Item"]=tk.Label(self.scrollable_frame,text="%i"%(len(self.ui_new_agreements)+1))
        row["Document/Desc"]=tk.Entry(self.scrollable_frame,width=25)
        #row["Document #"].insert(0, reg_number)
        row["Copies/Dept"]=tk.Entry(self.scrollable_frame,width=25)
        row["Signatories"]=tk.Entry(self.scrollable_frame,width=25)
        row["Condition of Approval"]=tk.Entry(self.scrollable_frame,width=25)
        #row["Signatories"].insert(0, signatories)
        row["Circulation Notes"]=tk.Entry(self.scrollable_frame,width=25)
        self.generate_dropdown("Status",self.app.get_document_tracking_statuses(),row)
        
        self.ui_new_agreements.append(row)

    def generate_dropdown(self,name,items,location,default=0):
        location["%s_Val"%name]=tk.StringVar()
        location[name]=ttk.Combobox(self.scrollable_frame,textvariable=location["%s_Val"%name], state="readonly") 
        location[name].bind("<MouseWheel>", self._dont_scroll)
        location[name]['values']=items
        location[name].set(items[0])

        def selection_changed(event):
            """
            This function is called when the combobox selection changes.
            """
            self.format_rows()

        location[name].bind("<<ComboboxSelected>>", selection_changed)

    def get_ui_state(self):
        ui_state = {
            "existing_encumbrances_on_title": [],
            "new_agreements": [],
            "plans": {}
        }

        # Header
        ui_state["header"] = {
            "program_name": __PROGRAM_NAME__,
            "program_version" : __VERSION_TEXT__,
            "file_version" : __FILE_VERSION__,
        }

        # Get Existing Encumbrances
        for row in self.ui_insts_on_title:
            data = {}
            for col in self.app.get_existing_inst_col_order():
                if col == "Item":
                    continue
                elif col in row:
                    data[col] = row[col].get()
                elif f"{col}_Val" in row:  # For dropdowns
                    data[col] = row[f"{col}_Val"].get()
            ui_state["existing_encumbrances_on_title"].append(data)

        # Get New Agreements
        for row in self.ui_new_agreements:
            data = {}
            for col in self.app.get_new_agreements_col_order():
                if col == "Item":
                    continue
                elif col in row:
                    data[col] = row[col].get()
                elif f"{col}_Val" in row:  # For dropdowns
                    data[col] = row[f"{col}_Val"].get()
            ui_state["new_agreements"].append(data)

        # Get Plans
        for plan_key, rows in self.ui_new_plans.items():
            ui_state["plans"][plan_key] = []
            for row in rows:
                data = {}
                for col in self.app.get_new_agreements_col_order():
                    if col == "Item":
                        continue
                    elif col in row:
                        data[col] = row[col].get()
                    elif f"{col}_Val" in row:  # For dropdowns
                        data[col] = row[f"{col}_Val"].get()
                ui_state["plans"][plan_key].append(data)

        return ui_state
    
    def load_ui_state(self, data):
        # Clear existing encumbrances
        for row in self.ui_insts_on_title:
            for widget in row.values():
                if hasattr(widget, "destroy"):
                    widget.destroy()
        self.ui_insts_on_title.clear()

        # Clear new agreements
        for row in self.ui_new_agreements:
            for widget in row.values():
                if hasattr(widget, "destroy"):
                    widget.destroy()
        self.ui_new_agreements.clear()

        # Clear plans
        for plan_rows in self.ui_new_plans.values():
            for row in plan_rows:
                for widget in row.values():
                    if hasattr(widget, "destroy"):
                        widget.destroy()
        self.ui_new_plans.clear()
        self.ui_new_plans_label.clear()
        self.ui_new_plans_header.clear()

        # Repopulate existing encumbrances
        for enc in data.get("existing_encumbrances_on_title", []):
            self.add_row_ex_enc(
                reg_number=enc.get("Document #", ""),
                reg_name=enc.get("Description", ""),
                signatories=enc.get("Signatories", "")
            )
            # Set dropdowns after widget is created
            row = self.ui_insts_on_title[-1]
            if "Action_Val" in row:
                row["Action_Val"].set(enc.get("Action", ""))
            if "Status_Val" in row:
                row["Status_Val"].set(enc.get("Status", ""))
            if "Circulation Notes" in row:
                row["Circulation Notes"].delete(0, tk.END)
                row["Circulation Notes"].insert(0, enc.get("Circulation Notes", ""))

        # Repopulate new agreements
        for agreement in data.get("new_agreements", []):
            self.add_row_new_agreement()
            row = self.ui_new_agreements[-1]
            for col in self.app.get_new_agreements_col_order():
                if col == "Item":
                    continue
                elif col in row:
                    row[col].delete(0, tk.END)
                    row[col].insert(0, agreement.get(col, ""))
                elif f"{col}_Val" in row:
                    row[f"{col}_Val"].set(agreement.get(col, ""))

        # Repopulate plans
        for plan_name, plan_rows in data.get("plans", {}).items():
            self.add_new_plan(plan_name)
            for i, row_data in enumerate(plan_rows):
                # If more rows are needed, add them
                while i >= len(self.ui_new_plans[plan_name]):
                    self.add_row_plan(self.ui_new_plans[plan_name])

                row = self.ui_new_plans[plan_name][i]
                for col in self.app.get_new_agreements_col_order():
                    if col == "Item":
                        continue
                    elif col in row:
                        row[col].delete(0, tk.END)
                        row[col].insert(0, row_data.get(col, ""))
                    elif f"{col}_Val" in row:
                        row[f"{col}_Val"].set(row_data.get(col, ""))

        self.regrid_rows()



if __name__ == "__main__":
    app = tkinterUI()
    app.mainloop()
