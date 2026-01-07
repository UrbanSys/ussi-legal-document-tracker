"""
Service for PDF processing and title document extraction.
Wraps the existing utils.py logic for use in the FastAPI routes.
"""
import re
import json
from typing import Dict, List, Any, Optional
from pypdf import PdfReader
from sqlalchemy.orm import Session
from app.models.title import TitleDocument, Encumbrance
from app.schemas.title import EncumbranceResponse


class PDFProcessorService:
    """Handles PDF title certificate processing and encumbrance extraction."""

    @staticmethod
    def process_title_cert(pdf_reader: PdfReader) -> Dict[str, Any]:
        """
        Process a PDF title certificate to extract legal description and instruments.
        
        Args:
            pdf_reader: PyPDF PdfReader instance with loaded document
            
        Returns:
            Dictionary with extracted data including legal_desc and inst_on_title
        """
        ret_dict = {}

        # Strip out page numbers/headers for easier processing
        stripped_document = ""
        for page in pdf_reader.pages:
            formatted_page = ""
            text = page.extract_text().splitlines()
            skip_counter = 0
            
            for idx, line in enumerate(text):
                should_include_line = True
                
                if line == "( CONTINUED )":
                    should_include_line = False
                if "---------" in line and idx == 0:
                    skip_counter = 8
                if "PAGE" == line and idx == 0:
                    skip_counter = 3
                if skip_counter > 0:
                    skip_counter -= 1
                    should_include_line = False
                    
                if should_include_line:
                    formatted_page = formatted_page + line + "\n"
                    
            stripped_document = stripped_document + formatted_page

        # Extract legal description
        text = stripped_document.splitlines()
        legal_desc_start_index = 0
        legal_desc_end_index = 0
        
        for idx, line in enumerate(text):
            if line == "LEGAL DESCRIPTION":
                legal_desc_start_index = idx + 1
            if line == "EXCEPTING THEREOUT ALL MINES AND MINERALS":
                legal_desc_end_index = idx
            if "ATS REFERENCE:" in line and legal_desc_end_index == 0:
                legal_desc_end_index = idx - 1

        legal_desc_text = ""
        if legal_desc_start_index != 0 and legal_desc_end_index != 0:
            for i in range(legal_desc_start_index, legal_desc_end_index + 1):
                legal_desc_text = legal_desc_text + text[i] + "\n"
            ret_dict["legal_desc"] = legal_desc_text
        else:
            raise ValueError("Unable to locate legal description in text!")
        
        # Extract document number 
        title_num_start_index = 0
        title_num_end_index = 0
        
        for idx, line in enumerate(text):
            if "TITLE NUMBER" in line:
                title_num_start_index = idx + 1
                print(text[title_num_start_index])

        if title_num_start_index!=0:
            print(title_num_start_index)
            print(text[title_num_start_index])
            title_num_text = text[title_num_start_index]

            m_linc = re.compile(r"\b\d{4}\s\d{3}\s\d{3}\b")
            m_short_legal = re.compile(r"\d{7}+(?:;\d+)+$")
            m_title_num = re.compile(r"\d{3}\s\d{3}\s\d{3}(?:\s*\+\d+)?")

            res_match = m_linc.search(title_num_text)
            result_linc = res_match.group()
            title_num_text = title_num_text.replace(result_linc,"",1)
            ret_dict["doc_linc"]=result_linc

            res_match = m_short_legal.search(title_num_text)
            result_short_legal = res_match.group()
            title_num_text = title_num_text.replace(result_short_legal,"",1)
            ret_dict["doc_short_legal"]=result_short_legal

            res_match = m_title_num.search(title_num_text)
            result_title_num = res_match.group()
            ret_dict["doc_title_num"]=result_title_num
        else:
            ValueError("Unable to locate legal description in text!")

        # Extract instruments on title
        m_rn = re.compile(r'[\d]{3} [\d]{3} [\d]{3}|\d{2,}[A-Za-z]{2,}')
        m_date = re.compile(r'[\d]{2}/[0-9]{2}/[\d]{4}')
        m_inst = re.compile(r'(?:[A-Z]{3,}(?: [A-Z]+)*)')
        
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
            line_for_rn = i
            result_date = m_date.search(i)
            if result_date:
                has_date=True
                temp_date = result_date.group()
                line_for_rn = i.replace(temp_date, " ")
            result_rn = m_rn.search(line_for_rn)
            if result_rn:
                has_rn=True
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

        ret_dict["inst_on_title"] = inst_on_title

        # Count instruments
        m_inst_count = re.compile(r'[\d]{3}')
        for idx, line in enumerate(text):
            if "TOTAL INSTRUMENTS:" in line:
                result_inst_count = m_inst_count.search(line)
                if result_inst_count:
                    inst_count_in_title = int(result_inst_count.group())
                    ret_dict["inst_count_in_title"] = inst_count_in_title
                    ret_dict["inst_count"] = len(inst_on_title)
                else:
                    raise ValueError("Cannot decipher the number of instruments listed on the TOTAL INSTRUMENTS line")

        return ret_dict


class TitleDocumentService:
    """Service for managing title documents in the database."""

    @staticmethod
    def save_extracted_data(
        db: Session,
        title_doc_id: int,
        extracted_data: Dict[str, Any]
    ) -> List[Encumbrance]:
        """
        Save extracted encumbrance data to the database.
        
        Args:
            db: Database session
            title_doc_id: ID of the title document
            extracted_data: Dictionary with extracted encumbrance data
            
        Returns:
            List of created Encumbrance objects
        """
        encumbrances = []
        
        for idx, inst in enumerate(extracted_data.get("inst_on_title", []), start=1):
            encumbrance = Encumbrance(
                title_document_id=title_doc_id,
                item_no=idx,
                document_number=inst.get("reg_number"),
                encumbrance_date=None,  # Parse from inst["date"] if needed
                description=inst.get("name"),
                signatories=inst.get("signatories"),
            )
            db.add(encumbrance)
            encumbrances.append(encumbrance)
        
        db.commit()
        return encumbrances
