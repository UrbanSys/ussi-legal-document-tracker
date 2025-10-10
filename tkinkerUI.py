"""
tkinkerUI.py
Gavin Schultz 2025
A prototype of the UI in tkinker
"""
import tkinter as tk
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

        row_labels = self.app.get_existing_inst_col_order()
        for col in row_labels:
            txt = tk.Label(self.scrollable_frame,text=col)
            self.ui_insts_on_title_header.append(txt)

        for i in range(0,10):
            txt = tk.Label(self.scrollable_frame,text="test %i"%i)
            input = tk.Entry(self.scrollable_frame)

            row = {}
            row[row_labels[0]]=txt
            row[row_labels[1]]=input
            self.ui_insts_on_title.append(row)

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

    def regrid_rows(self):
        for i, col_widgets in enumerate(self.ui_insts_on_title_header, start=1):
            col_widgets.grid(row=0, column=i)
        for i, row_widgets in enumerate(self.ui_insts_on_title, start=1):
            for j, col in enumerate(self.app.get_existing_inst_col_order(),start=1):
                if col in row_widgets:
                    row_widgets[col].grid(row=i, column=j)

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
                    row[widget].destroy()
            self.ui_insts_on_title = []
            insts_on_title = self.app.get_instruments_on_title()
            row_labels = self.app.get_existing_inst_col_order()
            for i, inst in enumerate(insts_on_title,start=1):
                """
                new_inst["date"] = inst_date
                new_inst["reg_number"] = inst_rn
                new_inst["name"] = inst_name
                new_inst["description"] = inst_text
                new_inst["signatories"] = sign_text
                new_inst["temp_selection"] = 4
                """
                row = {}
                row["Item"]=tk.Label(self.scrollable_frame,text="%i"%i)
                row["Document #"]=tk.Entry(self.scrollable_frame)
                row["Document #"].insert(0, inst["reg_number"])
                row["Description"]=tk.Entry(self.scrollable_frame)
                row["Description"].insert(0, inst["description"])
                row["Signatories"]=tk.Entry(self.scrollable_frame)
                row["Signatories"].insert(0, inst["signatories"])
                row["Action"]=tk.Entry(self.scrollable_frame)
                row["Circulation Notes"]=tk.Entry(self.scrollable_frame)
                row["Status"]=tk.Entry(self.scrollable_frame)
                self.ui_insts_on_title.append(row)
            
            mb.showinfo("Successfully imported title!","Inported %i of %i instruments"%(len(insts_on_title),self.app.get_loaded_insts_on_title()))
            self.regrid_rows()

if __name__ == "__main__":
    app = tkinkerUI()
    app.mainloop()
