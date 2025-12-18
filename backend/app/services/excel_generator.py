"""
Service for document generation from templates.
Wraps the existing templateGen.py logic for use in the FastAPI routes.
"""
from typing import Dict, Any, Optional
import xlsxwriter


class ExcelGeneratorService:
    """Handles generation of legal documents from templates."""

    @staticmethod
    def write_header_row(worksheet, row, col_width,format,text):
        worksheet.merge_range(row,0,row,col_width-1,text,format)

    @staticmethod
    def export_as_excel(fileobj,encumbrances = [], plans = {}, new_agreements = [],proj_num="0000.0000.00"):
        print("exporting")

        workbook = xlsxwriter.Workbook(fileobj, {"in_memory": True})
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
        ExcelGeneratorService.write_header_row(worksheet, row,7,title_format,"%s - PROJECT - DOCUMENT TRACKING"%proj_num)
        row += 1
        for plan_name, title in encumbrances.items():
            ExcelGeneratorService.write_header_row(worksheet, row,7,section_format,"EXISTING ENCUMBRANCES ON TITLE - %s"%plan_name)
            row += 1
            if len(title)>0:
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
            ExcelGeneratorService.write_header_row(worksheet, row,7,section_format,"PLAN - %s"%plan_name)
            row += 1
            if len(plan)>0:
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


        ExcelGeneratorService.write_header_row(worksheet, row,7,section_format,"NEW AGREEMENTS CONCURRENT WITH REGISTRATION")
        row += 1
        if len(new_agreements)>0:
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
