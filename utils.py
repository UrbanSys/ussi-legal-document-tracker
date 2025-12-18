"""
utils.py
Gavin Schultz 2025
Contains various methods to process data, including title docs, instruments, and data types
"""

import re
import xlsxwriter

class FileReadError(Exception):
    """Custom exception for file read errors."""
    pass

class ProjectStringError(Exception):
    """Custom exception for file read errors."""
    pass

"""
Processes a PDF of the title cert to extract information out if it
currently extracts the legal description and instruments on title
pdf_reader: PDF Reader currently open with a document to proces
returns: Dictionary with the legal description and instruments on title 
"""
def process_title_cert(pdf_reader):
    ret_dict = {}

    pages = pdf_reader.pages
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
    #print(stripped_document)
    
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
        ret_dict["legal_desc"]=legal_desc_text
    else:
        raise FileReadError("Unable to locate legal description in text! (Searching between %i and %i)"%(legal_desc_start_index,legal_desc_end_index))


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

    inst_on_title = []
    inst_page_number = 0

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

            inst_on_title.append(new_inst)

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

    ret_dict["inst_on_title"]=inst_on_title

    for idx, i in enumerate(text):
        if "TOTAL INSTRUMENTS:" in i:
            result_inst_count = m_inst_count.search(i)
            if result_inst_count:
                inst_count_in_title = int(result_inst_count.group())
                #print("Load Title File","%i of %i instruments on title have been successfully discovered!"%(len(inst_on_title),inst_count_in_title))
                ret_dict["inst_count_in_title"] = inst_count_in_title
                ret_dict["inst_count"] = len(inst_on_title)
            else: 
                raise FileReadError("Cannot decipher the number of instruments listed on the TOTAL INSTRUMENTS: line")
    return ret_dict

"""
Seperates the project number string into a tuple with 3 elements, being the client, project, and phase
projectnumber: String with the project number
returns: Tuple with properly formatted parts of a project number
"""    
def process_project_string(projectnumber):
		project_parts = projectnumber.split(".")
		if len(project_parts) !=3:
			raise ProjectStringError()
		if len(project_parts[0])>6:
			raise ProjectStringError()
		else:
			project_parts[0] = project_parts[0].zfill(6)

		if len(project_parts[1])>4:
			raise ProjectStringError()
		else:
			project_parts[1] = project_parts[1].zfill(4)

		if len(project_parts[2])>2:
			raise ProjectStringError()
		else:
			project_parts[2] = project_parts[2].zfill(2)

		#print("%s.%s.%s"%(project_parts[0],project_parts[1],project_parts[2]))
		return (project_parts[1],project_parts[2],project_parts[3])

def load_config(config_file):
    full_discharges = []
    partial_discharges = []
    consents = []
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
                        full_discharges.append(temp_dict)
                    elif command=="Partial Discharge":
                        partial_discharges.append(temp_dict)
                    elif command=="Consent":
                        consents.append(temp_dict)
                        
    except FileNotFoundError:
        print("Unable to read file!")

    return (full_discharges,partial_discharges,consents)

def export_as_excel(filename,encumbrances = [], plans = {}, new_agreements = [],proj_num="0000.0000.00"):
    print("exporting")

    #print(encumbrances)
    #print(plans)
    #print(new_agreements)
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    title_format = workbook.add_format(
        {
            "bold": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "#424242",
            "font_color": "white",
        }
    )

    section_format = workbook.add_format(
        {
            "bold": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "#CC9A62",
            "font_color": "black",
        }
    )

    base_format = workbook.add_format({"border": 1})

    worksheet.set_column("A:A", 25)
    worksheet.set_column("B:B", 25)
    worksheet.set_column("C:C", 40)
    worksheet.set_column("D:D", 40)
    worksheet.set_column("E:E", 28)
    worksheet.set_column("F:F", 45)
    worksheet.set_column("G:G", 33)

    action_options = ["NO ACTION REQUIRED","CONSENT","PARTIAL DISCHARGE","FULL_DISCHARGE"]
    options = ["---","Prepared","Complete","No Action Required","Client for Execution","City for Execution","Third party for Execution"]

    firstrow = 0
    lastrow = 0

    row = 0
    write_header_row(worksheet, row,7,title_format,"%s - PROJECT - DOCUMENT TRACKING"%proj_num)
    row += 1
    for plan_name, title in encumbrances.items():
        write_header_row(worksheet, row,7,section_format,"EXISTING ENCUMBRANCES ON TITLE - %s"%plan_name)
        row += 1
        table_keys = title[0].keys()
        worksheet.write(row,0,"Item #",title_format)
        for index, key in enumerate(table_keys):
            worksheet.write(row,index+1,key,title_format)
        firstrow = row+1
        row +=1
        for item_no, line in enumerate(title):
            worksheet.write(row,0,item_no+1,base_format)
            for index, key in enumerate(table_keys):
                if key in line:
                    if key == "Action":
                        line[key] = line[key].upper()
                    worksheet.write(row,index+1,line[key],base_format)
            row+=1
        lastrow = row-1
        
        worksheet.data_validation(
            "G%i:G%i"%(firstrow+1,lastrow+1),
            {
                "validate": "list",
                "source": options,
            },
        )

        worksheet.data_validation(
            "E%i:E%i"%(firstrow+1,lastrow+1),
            {
                "validate": "list",
                "source": action_options,
            },
        )

    for plan_name, plan in plans.items():
        write_header_row(worksheet, row,7,section_format,"PLAN - %s"%plan_name)
        row += 1
        table_keys = plan[0].keys()
        worksheet.write(row,0,"Item #",title_format)
        for index, key in enumerate(table_keys):
            worksheet.write(row,index+1,key,title_format)
        firstrow = row+1
        row +=1
        for item_no, line in enumerate(plan):
            worksheet.write(row,0,item_no+1,base_format)
            for index, key in enumerate(table_keys):
                if key in line:
                    worksheet.write(row,index+1,line[key],base_format)
            row+=1
        lastrow = row-1
        
        worksheet.data_validation(
            "G%i:G%i"%(firstrow+1,lastrow+1),
            {
                "validate": "list",
                "source": options,
            },
        )


    write_header_row(worksheet, row,7,section_format,"NEW AGREEMENTS CONCURRENT WITH REGISTRATION")
    row += 1
    table_keys = new_agreements[0].keys()
    worksheet.write(row,0,"Item #",title_format)
    for index, key in enumerate(table_keys):
        worksheet.write(row,index+1,key,title_format)
    firstrow = row+1
    row +=1
    for item_no, line in enumerate(new_agreements):
        worksheet.write(row,0,item_no+1,base_format)
        for index, key in enumerate(table_keys):
            if key in line:
                worksheet.write(row,index+1,line[key],base_format)
        row+=1

    lastrow = row-1
        
    worksheet.data_validation(
        "G%i:G%i"%(firstrow+1,lastrow+1),
        {
            "validate": "list",
            "source": options,
        },
    )


    prepared_fmt = workbook.add_format({"bg_color": "#C6FFAC"})
    complete_fmt  = workbook.add_format({"bg_color": "#8F8F8F"})
    client_fmt = workbook.add_format({"bg_color": "#FDF8CD"})

    # Apply conditional formatting (rows 1–100, columns A–G)
    worksheet.conditional_format(
        "A1:G100",
        {
            "type": "formula",
            "criteria": '=$G1="Prepared"',
            "format": prepared_fmt,
        },
    )

    worksheet.conditional_format(
        "A1:G100",
        {
            "type": "formula",
            "criteria": '=OR($G1="Complete",$G1="No Action Required")',
            "format": complete_fmt,
        },
    )

    worksheet.conditional_format(
        "A1:G100",
        {
            "type": "formula",
            "criteria": '=$G1="Client for Execution"',
            "format": client_fmt,
        },
    )

    workbook.close() 

def write_header_row(worksheet, row, col_width,format,text):
    worksheet.merge_range(row,0,row,col_width-1,text,format)