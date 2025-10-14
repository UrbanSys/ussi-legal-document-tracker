import tkinter as tk
import os
import shutil
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import subprocess
import sys
import re
import utils

IMPORTED_DOCX=0

try:	
	from docx import Document
	IMPORTED_DOCX=1
except:
	IMPORTED_DOCX=0

IMPORTED_PYPDF=0

try:	
	from pypdf import PdfReader
	IMPORTED_PYPDF=1
except:
	IMPORTED_PYPDF=0

DEFAULT_CONFIG = "Z:/Urban Survey/Calgary/Automation/discharge_consent_config.txt"
PROJECTS_FOLDER= "U:Projects_CAL/"
REGISTERED_LEGAL_DOCS_FOLDER = r'Z:\Urban Survey\Registered Legal Documents'


SURVAFF = "Z:\\Urban Survey\\Templates\\Automation\\SurfAff-SUB-URW-auto.docx"
CONSENT_REQUESTED = "Z:\\Urban Survey\\Templates\\Automation\\YYYY-MM-DD SUBDIVISION  PH CONSENT TO REGISTER A PLAN - With Corporate Seal-REQUESTED-Auto.docx"
CONSENT_OWNER = "z:\\Urban Survey\\Templates\\Automation\\YYYY-MM-DD SUBDIVISION  PH CONSENT TO REGISTER A PLAN - With Corporate Seal-OWNER-Auto.docx"

SURVEYORS = [
	{"name":"Meredith Bryan","ftp":"986"},
	{"name":"Cathy Wilson","ftp":"796"},
	{"name":"James Durant","ftp":"920"},
]

class Templates:
	def __init__(self, args=[]):
		self.tk = tk.Tk()
		self.tk.title("Consent Document Preparer")
		self.tk.minsize(width=800,height=620)
		self.load_config(DEFAULT_CONFIG)
		self.generate_gui()

		self.inst_on_title = []
		self.inst_page_number = 0

		global IMPORTED_DOCX

		if not IMPORTED_DOCX:
			result = mb.askyesno("Warning!","python-docx is not installed. would you like to install it?")
			if result:
				subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
				try:	
					from docx import Document
					IMPORTED_DOCX=True
					mb.showinfo("Info","Installed!")
				except:
					IMPORTED_DOCX=False
					mb.showerror("Info","Unable to install!")
	
		global IMPORTED_PYPDF

		if not IMPORTED_PYPDF:
			result = mb.askyesno("Warning!","pypdf is not installed. would you like to install it?")
			if result:
				subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
				try:	
					from pypdf import PdfReader
					IMPORTED_PYPDF=True
					mb.showinfo("Info","Installed!")
				except:
					IMPORTED_PYPDF=False
					mb.showerror("Info","Unable to install!")

		self.legal_desc_text = ""

		self.tk.mainloop()

	def print_selection(self):
		pass


	def load_config(self,config_file):
		self.full_discharges = []
		self.partial_discharges = []
		self.consents = []
		try:
			with open(config_file) as f:
				for x in f:
					line = x.rstrip().split("|")
					if len(line)>=2:
						command = line[0]

						municipality = "Other"

						if len(line) >=3:
							municipality = line[2]

						temp_dict = {
							"doc_type":line[0],
							"path":line[1].replace("\"",""),
							"municipality":municipality,
						}
						
						if command=="Full Discharge":
							self.full_discharges.append(temp_dict)
						elif command=="Partial Discharge":
							self.partial_discharges.append(temp_dict)
						elif command=="Consent":
							self.consents.append(temp_dict)
							
		except FileNotFoundError:
			print("Unable to read file!")
			mb.showerror("Unable to find Config File","The config file (with paths containing the legal document templates) can't be found! %s"%DEFAULT_CONFIG)
		

	def generate_gui(self):
		for widgets in self.tk.winfo_children():
			widgets.destroy()
		
		# Main GUI
		client_label = tk.Label(self.tk,text="Client Name",justify="left",anchor="w")
		client_label.grid(row=0, column=0)
		self.clientname = tk.Entry(self.tk,width=50)
		self.clientname.grid(row=0, column=1)
	

		project_label = tk.Label(self.tk,text="Project Number",justify="left",anchor="w")
		project_label.grid(row=1, column=0)
		self.projectnumber = tk.Entry(self.tk,width=50)
		self.projectnumber.grid(row=1, column=1)

		project_label = tk.Label(self.tk,text="Municipality",justify="left",anchor="w")
		project_label.grid(row=2, column=0)
		self.citylabel = tk.Entry(self.tk,width=50)
		self.citylabel.grid(row=2, column=1)

		selection_label = tk.Label(self.tk,text="Surveyor",justify="left",anchor="w")
		selection_label.grid(row=3, column=0)
		self.all_surveyors = tk.Listbox(self.tk, selectmode = "single",height=len(SURVEYORS),width=25,selectbackground="gray",exportselection=0) 
		for i in SURVEYORS:
			self.all_surveyors.insert(tk.END, i["name"])
		self.all_surveyors.grid(row=3, column=1)

		open_title_button = tk.Button(self.tk,text="Load Title File",command=self.read_title_doc)
		open_title_button.grid(row=5,column=0)
		self.title_file_label = tk.Label(self.tk,text="No Title Open",justify="left",wraplength=500,anchor="w")
		self.title_file_label.grid(row=5, column=1)

		project_label = tk.Label(self.tk,text="Legal Description",justify="left",anchor="w")
		project_label.grid(row=6, column=0)
		self.legal_desc = tk.Text(self.tk,width=80, height=8)
		self.legal_desc.grid(row=6, column=1)

		startbutton = tk.Button(self.tk,text="Process Existing Encumbrances",command=self.open_encubrances_gui)
		startbutton.grid(row=7,column=1)

		startbutton = tk.Button(self.tk,text="Process Plans to be registered",command=self.open_plans_registered_gui)
		startbutton.grid(row=8,column=1)

		# Existing Encumbrances GUI
		self.existing_enc_window = tk.Toplevel(self.tk)
		self.existing_enc_window.title("Existing Encumbrances")
		self.existing_enc_window.minsize(width=800,height=620)
		self.existing_enc_window.withdraw()
		self.existing_enc_window.protocol("WM_DELETE_WINDOW", self.existing_enc_window.withdraw)

		self.existing_enc_top_label = tk.Label(self.existing_enc_window,text="Encumbrance x/x",justify="left",anchor="w")
		self.existing_enc_top_label.grid(row=0,column=1)
		prevbutton = tk.Button(self.existing_enc_window,text="Delete Encumbrance",command=self.encumbrance_gui_delete)
		prevbutton.grid(row=0,column=0)

		reg_label = tk.Label(self.existing_enc_window,text="Registration Number",justify="left",anchor="w")
		reg_label.grid(row=1, column=0)
		self.existing_enc_reg = tk.Entry(self.existing_enc_window,width=50, validate = "key", validatecommand = self.update_encumbrance_values)
		self.existing_enc_reg.grid(row=1, column=1)

		date_label = tk.Label(self.existing_enc_window,text="Registration Date",justify="left",anchor="w")
		date_label.grid(row=2, column=0)
		self.existing_enc_reg_date = tk.Entry(self.existing_enc_window,width=50, validate = "key", validatecommand = self.update_encumbrance_values)
		self.existing_enc_reg_date.grid(row=2, column=1)

		name_label = tk.Label(self.existing_enc_window,text="Instrument Name",justify="left",anchor="w")
		name_label.grid(row=3, column=0)
		self.existing_enc_reg_name = tk.Entry(self.existing_enc_window,width=50, validate = "key", validatecommand = self.update_encumbrance_values)
		self.existing_enc_reg_name.grid(row=3, column=1)

		
		self.existing_enc_details_label = tk.Label(self.existing_enc_window,text="Details",justify="left",anchor="w")
		#self.existing_enc_details_label.grid(row=4, column=1)
		details_label = tk.Label(self.existing_enc_window,text="Details",justify="left",anchor="w")
		details_label.grid(row=4, column=0) 
		self.existing_enc_desc = tk.Text(self.existing_enc_window,width=80, height=8)
		self.existing_enc_desc.grid(row=4, column=1)
		self.existing_enc_desc.bind("<<Modified>>", self.update_encumbrance_values_event)
		
		signatories_label = tk.Label(self.existing_enc_window,text="Signatories",justify="left",anchor="w")
		signatories_label.grid(row=5, column=0)
		self.existing_enc_signs = tk.Text(self.existing_enc_window,width=80, height=8)
		self.existing_enc_signs.grid(row=5, column=1)
		self.existing_enc_signs.bind("<<Modified>>", self.update_encumbrance_values_event)

		selection_label = tk.Label(self.existing_enc_window,text="Action",justify="left",anchor="w")
		selection_label.grid(row=6, column=0)
		self.existing_enc_option = tk.Listbox(self.existing_enc_window, selectmode = "single",height=5,width=25,selectbackground="gray",exportselection=0) 
		self.existing_enc_option.insert(tk.END, "Full Discharge")
		self.existing_enc_option.insert(tk.END, "Partial Discharge")
		self.existing_enc_option.insert(tk.END, "Consent")
		self.existing_enc_option.insert(tk.END, "No Action Required") 
		self.existing_enc_option.insert(tk.END, "Further Action Required")
		self.existing_enc_option.grid(row=6, column=1)
		self.existing_enc_option.bind("<<ListboxSelect>>", self.update_encumbrance_selection_event)

		prevbutton = tk.Button(self.existing_enc_window,text="<-",command=self.encumbrance_gui_back)
		prevbutton.grid(row=7,column=0)
		prevbutton = tk.Button(self.existing_enc_window,text="Find and open document for this encumbrance",command=self.find_and_open_legal_doc)
		prevbutton.grid(row=7,column=1)
		prevbutton = tk.Button(self.existing_enc_window,text="->",command=self.encumbrance_gui_forward)
		prevbutton.grid(row=7,column=2)

		# Plans to be registered GUI
		self.newdocUI = tk.Toplevel(self.tk)
		self.newdocUI.title("Plans to be registered")
		self.newdocUI.minsize(width=800,height=1000)
		self.newdocUI.withdraw()
		self.newdocUI.protocol("WM_DELETE_WINDOW", self.newdocUI.withdraw)
 		
		root = self.newdocUI

		self.entries = []

        # Title
		tk.Label(root, text="Survey Dates").grid(row=0, column=1, pady=10)
		self.new_plans_dates_start = tk.Entry(root,width=30)
		self.new_plans_dates_start.grid(row=0,column=2)
		self.new_plans_dates_end = tk.Entry(root,width=30)
		self.new_plans_dates_end.grid(row=0,column=3)

        # Header Row
		headers = ["#", "Plan Code", "Legal Description", "Owner Consent", "City Consent"]
		for col, text in enumerate(headers):
			tk.Label(root, text=text).grid(row=1, column=col, padx=5, pady=5)

        # Data Rows
		for i in range(10):
			row_num = i + 2
			row_data = {}

			# Row number label
			tk.Label(root, text=f"{i+1}").grid(row=row_num, column=0, padx=5)

			# Plan Code
			plan_code_var = tk.StringVar()
			plan_code = tk.Entry(root, width=12, textvariable=plan_code_var)
			if i == 0:
				plan_code.insert(0, "SUB1")
			plan_code.grid(row=row_num, column=1, padx=5)
			plan_code.bind("<FocusOut>", lambda *args, index=i: self.newplan_edit_code(index))
			row_data['plan_code'] = plan_code
			row_data['plan_code_var'] = plan_code_var

			# Legal Description
			legal_desc = tk.Text(root, width=40, height=3)
			legal_desc.grid(row=row_num, column=2, padx=5, pady=5)
			row_data['legal_desc'] = legal_desc

			# Consent type (radio button behavior using IntVar)
			consent_var = tk.IntVar()
			owner_cb = tk.Checkbutton(root, variable=consent_var, onvalue=1, offvalue=0)
			owner_cb.grid(row=row_num, column=3)

			city_cb = tk.Checkbutton(root, variable=consent_var, onvalue=2, offvalue=0)
			city_cb.grid(row=row_num, column=4)

			if i == 0:
				consent_var.set(1)

			row_data['consent_var'] = consent_var

			self.entries.append(row_data)

        # Submit button
		submit_btn = tk.Button(root, text="Submit", command=self.submit_newplan)
		submit_btn.grid(row=13, column=0, columnspan=6, pady=15)

	def generate_gui_template_chooser(self, gui_choice):
		self.temp_picker = tk.Toplevel(self.tk)
		self.temp_picker.title("Document Picker")
		self.temp_picker.minsize(width=600,height=800)

		main_frame = tk.Frame(self.temp_picker)
		main_frame.pack(fill=tk.BOTH, expand=True)

		grouped = {}
		for item in gui_choice:
			muni = item["municipality"]
			file_name = os.path.basename(item["path"])
			grouped.setdefault(muni, []).append(file_name)

		canvas = tk.Canvas(main_frame)
		scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
		scrollable_frame = tk.Frame(canvas)

		scrollable_frame.bind(
			"<Configure>",
			lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
		)

		canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)

		canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")

		self.selected_file = tk.StringVar()
		self.selected_file.set(None)

		for municipality, paths in grouped.items():
			muni_label = tk.Label(scrollable_frame, text=municipality, font=('Arial', 12, 'bold'))
			muni_label.pack(anchor='w', pady=(10, 0))

			for path in paths:
				file_name = os.path.basename(path)
				rb = tk.Radiobutton(
					scrollable_frame,
					text=file_name,
					variable=self.selected_file,
					value=path
				)
				rb.pack(anchor='w', padx=20)

		submit_btn = tk.Button(self.temp_picker, text="Submit", command=self.submit)
		submit_btn.pack(pady=10)
		
		self.temp_picker.focus_force()
		
	def submit_newplan(self):
		print("Collected Entries:")

		folderpath = fd.askdirectory(
				)
		
		if not folderpath.endswith("/"):
			folderpath = folderpath+"/"

		for i, entry in enumerate(self.entries, start=1):
			code = entry['plan_code'].get()
			desc = entry['legal_desc'].get("1.0", tk.END).strip()
			consent_val = entry['consent_var'].get()

			consent_text = {
				1: "Owner Consent",
				2: "City Consent"
			}.get(consent_val, "None Selected")

			print(f"{i}. Plan Code: {code}, Legal Description: {desc}, Consent: {consent_text}")

			if (code!=""):

				clientname = self.clientname.get()
				projectnumber = self.projectnumber.get()
				city = self.citylabel.get()

				d_start = self.new_plans_dates_start.get()
				d_end = self.new_plans_dates_end.get()

				drawing = projectnumber.replace(".", "")+"-"+code 

				surveyor = ""
				ftpnum = ""

				shortcode = re.sub(r'\d+', '', code).upper()
				print(shortcode)
				plantype = "PLAN TYPE"
				plan_folder = folderpath + code + "/"

				try:
					os.makedirs(plan_folder, exist_ok=True)
				except OSError as e:
					print(f"Error creating folder '{plan_folder}': {e}")
			
				if (shortcode=="SUB"):
					plantype = "Subdivision"

				elif (shortcode=="URW"):
					plantype = "Utility Right of Way"

				elif (shortcode=="ODRW"):
					plantype = "Overland Drainage Right of Way"

				elif (shortcode=="MARW"):
					plantype = "Maintenance Access Right of Way"

				elif (shortcode=="SRW"):
					plantype = "Screening Fence Access Right of Way"

				elif (shortcode=="PRW"):
					plantype = "Dual Services Pocket Easements"


				elif len(self.all_surveyors.curselection())>0:
					index = self.all_surveyors.curselection()[0]
					surveyor = SURVEYORS[index]["name"]
					ftpnum = SURVEYORS[index]["ftp"]
					print(surveyor)

				filepath_surfaiff = plan_folder+"surfaif.docx"
				filepath_consent = plan_folder+"consent.docx"
				
				self.generate_surveyor_aff(SURVAFF, surveyor, ftpnum, projectnumber, drawing, desc,d_start,d_end, "Calgary", filepath_surfaiff)

				if (consent_val==1):
					self.generate_consent_wseal(CONSENT_OWNER,clientname,plantype,surveyor,drawing,desc,filepath_consent)
				elif (consent_val==2):
					self.generate_consent_wseal(CONSENT_REQUESTED,city,plantype,surveyor,drawing,desc,filepath_consent)

	def get_config_file(self):
		path = fd.askopenfilename()
		if path:
			print(path)
			self.load_config(path)

	def read_title_doc(self):
		self.existing_enc_window.withdraw()
		filepath = fd.askopenfilename(
            title="Open File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
		if filepath:
			reader = PdfReader(filepath)
			self.title_file_label['text'] = filepath
			self.process_title_cert(reader.pages)

	def submit(self):
		chosen = self.selected_file.get()
		if chosen:
			print("Selected file:", chosen)
			mb.showinfo("Selected file:", chosen)
		else:
			print("No file selected.")

	def open_plans_registered_gui(self):
		self.newdocUI.deiconify()

	def open_encubrances_gui(self):
		if len(self.inst_on_title) == 0:
			result = mb.askyesno("No Instruments on Title","No Instruments on title have been loaded. Proceed with manual entry?")
			if result:
				self.inst_on_title.append(self.create_empty_inst())
			else:
				return
		self.existing_enc_window.deiconify()
		self.update_encumrances_gui()

	def update_encumrances_gui(self):
		self.can_update_values = False
		cur_inst = self.inst_on_title[self.inst_page_number]

		self.existing_enc_top_label["text"] = "Encumbrance %i/%i"%(self.inst_page_number+1,len(self.inst_on_title))

		self.existing_enc_reg.delete(0, tk.END)
		self.existing_enc_reg.insert(0, cur_inst["reg_number"])

		self.existing_enc_reg_date.delete(0, tk.END)
		self.existing_enc_reg_date.insert(0, cur_inst["date"])

		self.existing_enc_reg_name.delete(0, tk.END)
		self.existing_enc_reg_name.insert(0, cur_inst["name"])

		self.existing_enc_desc.delete("1.0", tk.END)
		self.existing_enc_desc.insert("1.0", cur_inst["description"].rstrip())

		self.existing_enc_details_label["text"] = cur_inst["description"]

		self.existing_enc_signs.delete("1.0", tk.END)
		self.existing_enc_signs.insert("1.0", cur_inst["signatories"].rstrip())

		self.existing_enc_option.selection_clear(0, tk.END)
		self.existing_enc_option.selection_set(cur_inst["temp_selection"])
		

		self.can_update_values = True

	def encumbrance_gui_back(self):
		if self.inst_page_number>0:
			self.inst_page_number-=1
			self.update_encumrances_gui()

	def encumbrance_gui_forward(self):
		if self.inst_page_number<len(self.inst_on_title)-1:
			self.inst_page_number+=1
			self.update_encumrances_gui()
		else:
			result = mb.askyesno("Create New Encumbrance","You are on the last encumbrance. Create a new one? ",parent=self.existing_enc_window)
			if result:
				self.inst_on_title.append(self.create_empty_inst())
				self.inst_page_number+=1
				self.update_encumrances_gui()

	def encumbrance_gui_delete(self):
		result = mb.askyesno("Delete Encumbrance","Are you sure you would like to delete the current encumbrance? ",parent=self.existing_enc_window)		
		if result:
			del self.inst_on_title[self.inst_page_number]
			if len(self.inst_on_title)==0:
				self.inst_on_title.append(self.create_empty_inst())
			self.inst_page_number-=1
			if self.inst_page_number<0:
				self.inst_page_number=0
			self.update_encumrances_gui()

	def update_encumbrance_values_event(self,event):
		text_wdg = event.widget
		if text_wdg.edit_modified():
			self.update_encumbrance_values()
			text_wdg.edit_modified(False)  # Reset the modified flag

	def update_encumbrance_selection_event(self,event):
		self.update_encumbrance_values()
		cur_sel = self.inst_on_title[self.inst_page_number]["temp_selection"]
		if cur_sel==0:
			self.generate_gui_template_chooser(self.full_discharges)
		elif cur_sel==1:
			self.generate_gui_template_chooser(self.partial_discharges)
		elif cur_sel==2:
			self.generate_gui_template_chooser(self.consents)

	def find_and_open_legal_doc(self):
		reg_num = self.inst_on_title[self.inst_page_number]["reg_number"]
		reg_num_stripped = reg_num.replace(' ','')
		if len(reg_num_stripped)<3:
			return
		contents = os.listdir(REGISTERED_LEGAL_DOCS_FOLDER)
		found = False
		for i in contents:
			if reg_num_stripped in i:
				found = True
				os.startfile(REGISTERED_LEGAL_DOCS_FOLDER+'/'+i)
		if not found:
			result = mb.showwarning("Cannot find Encumbrance","Unable to find encumbrance in the Registered Legal Documents folder! (%s) Perhaps it hasn't been ordered or saved there?"%REGISTERED_LEGAL_DOCS_FOLDER,parent=self.existing_enc_window)


	def update_encumbrance_values(self):
		if self.can_update_values:
			cur_inst = self.inst_on_title[self.inst_page_number]
			cur_inst["reg_number"] = self.existing_enc_reg.get()
			cur_inst["date"] = self.existing_enc_reg_date.get()
			cur_inst["name"] = self.existing_enc_reg_name.get()
			cur_inst["description"] = self.existing_enc_desc.get("1.0", 'end')
			cur_inst["signatories"] = self.existing_enc_signs.get("1.0",'end')
			if len(self.existing_enc_option.curselection())>0:
				cur_inst["temp_selection"] = self.existing_enc_option.curselection()[0]
			else:
				cur_inst["temp_selection"] = 0
			#print("Updated %i"%self.inst_page_number)
		return True
	
	def newplan_edit_code(self,index):
		entry_data = self.entries[index]
		code = entry_data['plan_code_var'].get()
		print(f"Plan Code changed in row {index+1}: {code}")
		shortcode = re.sub(r'\d+', '', code).upper()

		consent_val = entry_data['consent_var']

		if shortcode=="SUB":
			#Owners Consent
			consent_val.set(1)

		elif shortcode=="URW":
			consent_val.set(2)

		elif shortcode=="ODRW":
			consent_val.set(2)

		elif shortcode=="MARW":
			consent_val.set(1)

		elif shortcode=="SRW":
			consent_val.set(2)

		elif shortcode=="PRW":
			consent_val.set(1)
	
	def create_empty_inst(self):
		return {
    		"date": "",
    		"reg_number": "",
    		"name": "",
    		"description": "",
			"temp_selection": 4,
			"signatories": ""
		}
	


	def generate_surveyor_aff(self, path, surveyor, ftp, file, drawing, legaldesc, startdate, enddate, surv_city,out):
		doc = Document(path)

		self.doc_find_and_replace(doc,r"%SURVEYOR%",surveyor)
		self.doc_find_and_replace(doc,r"%FTP%",ftp)
		self.doc_find_and_replace(doc,r"%FILE%",file)
		self.doc_find_and_replace(doc,r"%DRAWING%",drawing)
		self.doc_find_and_replace(doc,r"%LEGALDESC%",legaldesc)
		self.doc_find_and_replace(doc,r"%STARTDATE%",startdate)
		self.doc_find_and_replace(doc,r"%ENDDATE%",enddate)
		self.doc_find_and_replace(doc,r"%SURVEYORCITY%",surv_city)

		# Save the modified document
		doc.save(out)

	def generate_consent_wseal(self, path, corp, plantype, surveyor, filenumber, legal,out):
		doc = Document(path)

		self.doc_find_and_replace(doc,r"%SURVEYOR%",surveyor)
		self.doc_find_and_replace(doc,r"%CORPORATION%",corp)
		self.doc_find_and_replace(doc,r"%FILENUMBER%",filenumber)
		self.doc_find_and_replace(doc,r"%LEGAL%",legal)
		self.doc_find_and_replace(doc,r"%PLANTYPE%",plantype)

		# Save the modified document
		doc.save(out)

			
	def process_project_string(self,projectnumber):
		project_parts = projectnumber.split(".")
		if len(project_parts) !=3:
			return None
		if len(project_parts[0])>6:
			return None
		else:
			project_parts[0] = project_parts[0].zfill(6)

		if len(project_parts[1])>4:
			return None
		else:
			project_parts[1] = project_parts[1].zfill(4)

		if len(project_parts[2])>2:
			return None
		else:
			project_parts[2] = project_parts[2].zfill(2)

		#print("%s.%s.%s"%(project_parts[0],project_parts[1],project_parts[2]))
		return project_parts
	
	def process_title_cert(self,pages):
		# Strip out page numbers/headers etc. for easier processing
		stripped_document = ""
		for page in pages:
			formatted_page = ""
			#print("PAGE============================")
			text = page.extract_text().splitlines()
			skip_counter = 0
			for idx, i in enumerate(text):
				#print("t %s"%i)
				should_include_line = True
				if i=="( CONTINUED )":
					should_include_line = False
				if "---------" in i and idx==0:
					skip_counter =8
				if "PAGE"== i and idx==0:
					skip_counter =3
				if skip_counter>0:
					skip_counter-=1
					should_include_line = False
				if should_include_line:
					formatted_page = formatted_page + i + "\n"
			stripped_document = stripped_document + formatted_page
		print(stripped_document)
		
		# Identify important parts of the document
		# Legal Description
		text = stripped_document.splitlines()
		legal_desc_start_index = 0
		legal_desc_end_index = 0
		for idx, i in enumerate(text):
			if i == "LEGAL DESCRIPTION":
				legal_desc_start_index = idx+1
			if i == "EXCEPTING THEREOUT ALL MINES AND MINERALS":
				legal_desc_end_index = idx
			if "ATS REFERENCE:" in i and legal_desc_end_index==0:
				legal_desc_end_index = idx-1
		legal_desc_text = ""
		if legal_desc_start_index!=0 and legal_desc_end_index!=0:
			for i in range(legal_desc_start_index,legal_desc_end_index+1):
				legal_desc_text = legal_desc_text + text[i] + "\n"
			#mb.showinfo("legal description",legal_desc_text)
			print(legal_desc_text)
			self.legal_desc_text = legal_desc_text
			self.legal_desc.delete('1.0', tk.END)
			self.legal_desc.insert('1.0', legal_desc_text)
		else:
			mb.showerror("Error reading Instrument","Unable to locate legal description in text! %i %i"%(legal_desc_start_index,legal_desc_end_index))
			return


		# Instruments  
		m_rn = re.compile(r'[\d]{3} [\d]{3} [\d]{3}')
		m_date = re.compile(r'[\d]{2}/[0-9]{2}/[\d]{4}')
		m_inst = re.compile(r'(?:[A-Z]+ ?)+')
		
		inst_start_index = 0
		inst_end_index = 0

		inst_count = 0

		inst_date = ""
		inst_rn = ""
		inst_name = ""

		self.inst_on_title = []
		self.inst_page_number = 0

		for idx, i in enumerate(text):
			has_date=False
			has_rn=False
			end_of_inst = False
			result_rn = m_rn.search(i)
			if result_rn:
				has_rn=True
			result_date = m_date.search(i)
			if result_date:
				has_date=True
			if "TOTAL INSTRUMENTS" in i:
				end_of_inst = True
			if has_rn and has_date:
				#This is an instrument
				if inst_start_index!=0:
					end_of_inst = True

			if end_of_inst:
				inst_end_index=idx-1
				inst_text = ""
				sign_text = ""
				for j in range(inst_start_index+1,inst_end_index+1):
					inst_text = inst_text + text[j] + "\n"
					if "GRANTEE" in text[j] or "CAVEATOR" in text[j] or "MORTGAGEE" in text[j]:
						signatory = text[j].split(' - ')[1]
						sign_text = sign_text + signatory + "\n"
				#mb.showinfo("inst",inst_date+"\n"+inst_rn+"\n"+inst_name+"\n"+inst_text)

				new_inst = {}

				new_inst["date"] = inst_date
				new_inst["reg_number"] = inst_rn
				new_inst["name"] = inst_name
				new_inst["description"] = inst_text
				new_inst["signatories"] = sign_text
				new_inst["temp_selection"] = 4

				self.inst_on_title.append(new_inst)

				print(new_inst)

			if has_rn and has_date:
				#This line is the beginning of an instrument
				inst_date = result_date.group()
				inst_rn = result_rn.group()
				inst_start_index=idx
				result_name = m_inst.search(i)

				if result_name:
					inst_name = result_name.group()
				else:
					inst_name = "---------------"

		# Count the # of instruments
		m_inst_count = re.compile(r'[\d]{3}')

		for idx, i in enumerate(text):
			if "TOTAL INSTRUMENTS:" in i:
				result_inst_count = m_inst_count.search(i)
				if result_inst_count:
					inst_count_in_title = int(result_inst_count.group())
					mb.showinfo("Load Title File","%i of %i instruments on title have been successfully discovered!"%(len(self.inst_on_title),inst_count_in_title))
				else: 
					mb.showerror("Error reading Instrument","Cannot decipher the number of instruments listed on the TOTAL INSTRUMENTS: line")

			

if __name__ == '__main__':
	p = Templates([])