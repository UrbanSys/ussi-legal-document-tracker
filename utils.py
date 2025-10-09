import re


class FileReadError(Exception):
    """Custom exception for file read errors."""
    pass

"""
pdf_reader: PDF Reader currently open with a document to proces
"""
def process_title_cert(pdf_reader):
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
        ##TODO: PUT THIS IN A DESCRIPTION TO RETURN
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
                print("Load Title File","%i of %i instruments on title have been successfully discovered!"%(len(self.inst_on_title),inst_count_in_title))
            else: 
                raise FileReadError("Cannot decipher the number of instruments listed on the TOTAL INSTRUMENTS: line")