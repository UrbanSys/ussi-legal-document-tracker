"""
tkinkerUI.py
Gavin Schultz 2025
A prototype of the UI in tkinker
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from actions import DocTrackerActions
from tkinter import filedialog as fd

try:
    import genVersionNumber
    genVersionNumber.gen_version_info()
    from version_info import __VERSION_TEXT__
except ImportError:
    __VERSION_TEXT__ = "***version info unavalible***"

class tkinkerUI(tk.Tk):
    def __init__(self):
        super().__init__()

        main_view = tk.Frame(self)
        main_view.pack(side="top",fill="both", expand=True)
        bottom_view = tk.Frame(self)
        bottom_view.pack(side="bottom")

        build_text = __VERSION_TEXT__
        self.title("USSI Document Tracker - %s"%build_text)
        self.geometry("1000x600")

        self.app = DocTrackerActions()

        #Main view
        canvas = tk.Canvas(main_view)
        scrollbar = tk.Scrollbar(main_view, orient="vertical", command=canvas.yview)
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
        button = tk.Button(bottom_view,text="Button",command=self.dummy)
        button.grid(row=0, column=1)

        self.regrid_rows()

    def _on_mousewheel(self, event):
        # On Windows and Mac, event.delta is multiples of 120
        self.scrollable_frame.update_idletasks()  # Make sure layout updated
        self.scrollable_frame.master.yview_scroll(int(-1*(event.delta/120)), "units")

    def _dont_scroll(self,event):
        self._on_mousewheel(event)
        return "break"

    def regrid_rows(self):
        rid = 0
        self.ui_insts_on_title_label.grid(row=rid, column=0, columnspan=5, sticky="w")
        rid+=1
        for i, col_widgets in enumerate(self.ui_insts_on_title_header, start=1):
            col_widgets.grid(row=rid, column=i)
        rid+=1
        for i, row_widgets in enumerate(self.ui_insts_on_title, start=rid):
            for j, col in enumerate(self.app.get_existing_inst_col_order(),start=1):
                if col in row_widgets:
                    row_widgets[col].grid(row=i, column=j)
            rid  +=1

        for plan_key in self.ui_new_plans:
            self.ui_new_plans_label[plan_key].grid(row=rid, column=0, columnspan=5, sticky="w")
            rid+=1
            for i, col_widgets in enumerate(self.ui_new_plans_header[plan_key], start=1):
                col_widgets.grid(row=rid, column=i)
            rid+=1
            for i, row_widgets in enumerate(self.ui_new_plans[plan_key], start=rid):
                for j, col in enumerate(self.app.get_new_agreements_col_order(),start=1):
                    if col in row_widgets:
                        row_widgets[col].grid(row=i, column=j)
                rid  +=1

        self.ui_new_agreements_label.grid(row=rid, column=0, columnspan=5, sticky="w")
        rid+=1
        for i, col_widgets in enumerate(self.ui_new_agreements_header, start=1):
            col_widgets.grid(row=rid, column=i)
        rid+=1
        for i, row_widgets in enumerate(self.ui_new_agreements, start=rid):
            for j, col in enumerate(self.app.get_new_agreements_col_order(),start=1):
                if col in row_widgets:
                    row_widgets[col].grid(row=i, column=j)
            rid  +=1



    def dummy(self):
        mb.showinfo("message","message")

    def load_instruments_on_title(self):
        filepath = fd.askopenfilename(
            title="Open File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filepath:
            self.app.load_instruments_on_title(filepath)
            for row in self.ui_insts_on_title:
                for widget in row:
                    try:
                        row[widget].destroy()
                    except:
                        row[widget] = None
            self.ui_insts_on_title = []
            insts_on_title = self.app.get_instruments_on_title()
            row_labels = self.app.get_existing_inst_col_order()
            for i, inst in enumerate(insts_on_title,start=1):
                self.add_row_ex_enc(inst["reg_number"],inst["name"],inst["signatories"])
            
            mb.showinfo("Successfully imported title!","Inported %i of %i instruments"%(len(insts_on_title),self.app.get_loaded_insts_on_title()))
            self.regrid_rows()

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
        row["Item"]=tk.Label(self.scrollable_frame,text="%i"%(len(self.ui_new_agreements)+1))
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

if __name__ == "__main__":
    app = tkinkerUI()
    app.mainloop()
