"""
tkinkerUI.py
Gavin Schultz 2025
A prototype of the UI in tkinker
"""
import tkinter as tk
from tkinter import messagebox as mb
from actions import DocTrackerActions

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
        self.geometry("1000x900")

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

        self.ui_insts_on_title = []

        for i in range(0,10):
            txt = tk.Label(self.scrollable_frame,text="test %i"%i)
            input = tk.Entry(self.scrollable_frame)

            row = {}
            row["txt"]=txt
            row["input"]=input
            self.ui_insts_on_title.append(row)

        #Bottom bar
        button = tk.Button(bottom_view,text="Button",command=self.dummy)
        button.grid(row=0, column=0)

        self.regrid_rows()

    def _on_mousewheel(self, event):
        # On Windows and Mac, event.delta is multiples of 120
        self.scrollable_frame.update_idletasks()  # Make sure layout updated
        self.scrollable_frame.master.yview_scroll(int(-1*(event.delta/120)), "units")

    def regrid_rows(self):
        for i, row_widgets in enumerate(self.ui_insts_on_title, start=1):
            #for i in self.app_data.get_instruments_on_title:
            #    pass
            row_widgets["txt"].grid(row=i, column=1)
            row_widgets["input"].grid(row=i, column=2)

    def dummy(self):
        mb.showinfo("message","message")

if __name__ == "__main__":
    app = tkinkerUI()
    app.mainloop()
