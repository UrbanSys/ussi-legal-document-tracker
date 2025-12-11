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

        # Extract instruments on title
        m_rn = re.compile(r'[\d]{3} [\d]{3} [\d]{3}')
        m_date = re.compile(r'[\d]{2}/[0-9]{2}/[\d]{4}')
        m_inst = re.compile(r'(?:[A-Z]+ ?)+')

        inst_on_title = []
        inst_start_index = 0
        inst_end_index = 0
        inst_count_in_title = 0

        for idx, line in enumerate(text):
            has_date = False
            has_rn = False
            end_of_inst = False

            result_rn = m_rn.search(line)
            if result_rn:
                has_rn = True

            result_date = m_date.search(line)
            if result_date:
                has_date = True

            if "TOTAL INSTRUMENTS" in line:
                end_of_inst = True

            if has_rn and has_date and inst_start_index != 0:
                end_of_inst = True

            if end_of_inst and inst_start_index != 0:
                inst_end_index = idx - 1
                inst_text = ""
                sign_text = ""
                
                for j in range(inst_start_index + 1, inst_end_index + 1):
                    inst_text = inst_text + text[j] + "\n"
                    if "GRANTEE" in text[j] or "CAVEATOR" in text[j] or "MORTGAGEE" in text[j]:
                        try:
                            signatory = text[j].split(' - ')[1]
                            sign_text = sign_text + signatory + "\n"
                        except IndexError:
                            pass

                new_inst = {
                    "date": inst_date if inst_start_index != 0 else "",
                    "reg_number": inst_rn if inst_start_index != 0 else "",
                    "name": inst_name if inst_start_index != 0 else "",
                    "description": inst_text,
                    "signatories": sign_text,
                }
                inst_on_title.append(new_inst)

            if has_rn and has_date:
                inst_date = result_date.group()
                inst_rn = result_rn.group()
                inst_start_index = idx
                
                result_name = m_inst.search(line)
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
                description=inst.get("description"),
                signatories=inst.get("signatories"),
            )
            db.add(encumbrance)
            encumbrances.append(encumbrance)
        
        db.commit()
        return encumbrances
