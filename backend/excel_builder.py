"""
Excel Workbook Generator for JainBiz Lead Miner.
Optimized for direct, zero-thinking copy-paste into JainForJain.com listing forms.
Features auto-filters, clickable photo links, color-coded badges, and 3-paragraph descriptions.
"""

import os
from typing import List, Dict, Any
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generate_leads_excel(records: List[Dict[str, Any]], output_path: str, category: str = "", scope: str = "") -> str:
    """
    Generates a beautifully styled Excel workbook tailored directly to JainForJain.com fields.
    """
    wb = Workbook()
    
    # ------------------ SHEET 1: JAINFORJAIN LISTINGS ------------------
    ws = wb.active
    ws.title = "JainForJain Data Entry Leads"
    
    # Header Styles
    header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1E1B4B", end_color="1E1B4B", fill_type="solid") # Dark Indigo
    
    # Body Styles
    data_font = Font(name="Segoe UI", size=9, color="1E293B")
    owner_font = Font(name="Segoe UI", size=9, bold=True, color="4338CA") # Indigo bold
    cat_font = Font(name="Segoe UI", size=9, bold=True, color="0F766E")   # Teal bold
    link_font = Font(name="Segoe UI", size=9, color="2563EB", underline="single")
    desc_font = Font(name="Segoe UI", size=8, color="334155")
    
    tier_100_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid") # Soft Emerald
    tier_100_font = Font(name="Segoe UI", size=9, bold=True, color="166534")
    
    tier_85_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # Soft Amber
    tier_85_font = Font(name="Segoe UI", size=9, bold=True, color="92400E")
    
    tier_70_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    tier_70_font = Font(name="Segoe UI", size=9, color="475569")
    
    thin_border_side = Side(border_style="thin", color="E2E8F0")
    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    
    headers = [
        "Sl.",
        "Business / Firm Name",
        "JainForJain Category",
        "Owner / Contact Person",
        "Calling Number",
        "WhatsApp Number",
        "Email ID",
        "Address (Street & Locality)",
        "City",
        "State",
        "Pincode",
        "Google Maps URL",
        "Website URL",
        "Storefront Photo (Click HD)",
        "Auto-Generated Description (Ready to Paste)",
        "Verification Status",
        "Proof / Match Reason"
    ]
    
    ws.append(headers)
    
    # Style Headers
    for col_num in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = cell_border
        
    ws.row_dimensions[1].height = 32
    
    # Populate Rows
    for idx, rec in enumerate(records, start=1):
        row_num = idx + 1
        firm_name = rec.get("name", "N/A")
        j4j_cat = rec.get("j4j_category", "Business & Industry")
        owner_name = rec.get("owner", "Proprietor")
        phone = rec.get("phone", "Not Listed")
        whatsapp = rec.get("whatsapp", phone)
        email = rec.get("email", "")
        address = rec.get("address", "N/A")
        city = rec.get("city", "N/A")
        state = rec.get("state", "N/A")
        pincode = rec.get("pincode", "N/A")
        maps_url = rec.get("maps_url", "")
        website = rec.get("website", "")
        photo_url = rec.get("photo_url", "")
        desc = rec.get("description", "")
        tier = rec.get("tier", "⚪ 70% Lead Match")
        reason = rec.get("reason", "Category Correlation")
        
        row_values = [
            idx,
            firm_name,
            j4j_cat,
            owner_name,
            phone,
            whatsapp,
            email,
            address,
            city,
            state,
            pincode,
            "Open Google Map" if maps_url else "",
            "Visit Website" if website else "",
            "📸 View Storefront Photo" if photo_url else "No Photo",
            desc,
            tier,
            reason
        ]
        
        ws.append(row_values)
        ws.row_dimensions[row_num].height = 45 # Breathing room for 3-line description preview
        
        # Apply Cells Styling
        for col_idx in range(1, len(row_values) + 1):
            cell = ws.cell(row=row_num, column=col_idx)
            cell.font = data_font
            cell.border = cell_border
            cell.alignment = Alignment(vertical="center")
            
            # Align center for index, phone, city, state, pincode
            if col_idx in [1, 5, 6, 9, 10, 11]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                
            # Style Category column (Col 3)
            if col_idx == 3:
                cell.font = cat_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Style Owner column (Col 4)
            if col_idx == 4:
                cell.font = owner_font

            # Style Hyperlinks
            if col_idx == 12 and maps_url:
                cell.hyperlink = maps_url
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 13 and website:
                cell.hyperlink = website
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 14 and photo_url:
                cell.hyperlink = photo_url
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Style Description column (Col 15)
            if col_idx == 15:
                cell.font = desc_font
                cell.alignment = Alignment(vertical="top", wrap_text=True)

            # Style Verification Status Badge (Col 16)
            if col_idx == 16:
                if "100%" in tier:
                    cell.fill = tier_100_fill
                    cell.font = tier_100_font
                elif "85%" in tier:
                    cell.fill = tier_85_fill
                    cell.font = tier_85_font
                else:
                    cell.fill = tier_70_fill
                    cell.font = tier_70_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

    # Column Widths optimized for data entry workflow
    widths = {
        "A": 6,   # Sl.
        "B": 28,  # Firm Name
        "C": 22,  # J4J Category
        "D": 22,  # Owner
        "E": 18,  # Calling
        "F": 18,  # WhatsApp
        "G": 22,  # Email
        "H": 36,  # Address
        "I": 14,  # City
        "J": 14,  # State
        "K": 12,  # Pincode
        "L": 18,  # Maps Link
        "M": 18,  # Website
        "N": 22,  # Photo Link
        "O": 55,  # Description
        "P": 18,  # Verification Status
        "Q": 26   # Proof Reason
    }
    
    for col_letter, width in widths.items():
        ws.column_dimensions[col_letter].width = width
    
    # Enable AutoFilter across all headers
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{len(records) + 1}"

    # ------------------ SHEET 2: SUMMARY & STATS ------------------
    ws_summary = wb.create_sheet(title="Executive Summary")
    ws_summary.append(["JainForJain Lead Extraction Summary"])
    ws_summary["A1"].font = Font(name="Segoe UI", size=14, bold=True, color="1E1B4B")
    
    total_firms = len(records)
    verified_100 = sum(1 for r in records if "100%" in r.get("tier", ""))
    high_85 = sum(1 for r in records if "85%" in r.get("tier", ""))
    with_phones = sum(1 for r in records if r.get("phone") and r.get("phone") != "Not Listed")
    with_pincodes = sum(1 for r in records if r.get("pincode") and r.get("pincode") != "N/A")
    with_photos = sum(1 for r in records if r.get("photo_url"))
    
    metrics = [
        ["Target Category", category or "All Commercial"],
        ["Geographic Scope", scope or "Pan India"],
        ["Total Leads Extracted", total_firms],
        ["🟢 100% Confirmed Jain Firms", verified_100],
        ["🟡 85% High Match (Surname/Cluster)", high_85],
        ["Active Calling & WhatsApp Numbers", with_phones],
        ["Extracted 6-Digit Postal Pincodes", with_pincodes],
        ["Ready-to-Upload Storefront Photos", with_photos],
        ["Synthesized Ready-to-Paste Descriptions", total_firms]
    ]
    
    ws_summary.append([])
    for metric in metrics:
        ws_summary.append(metric)
        
    for row in ws_summary.iter_rows(min_row=3, max_row=11, min_col=1, max_col=2):
        for cell in row:
            cell.font = Font(name="Segoe UI", size=11)
            cell.border = cell_border
            if cell.column == 1:
                cell.font = Font(name="Segoe UI", size=11, bold=True, color="334155")
                cell.fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
                
    ws_summary.column_dimensions["A"].width = 38
    ws_summary.column_dimensions["B"].width = 25
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    return output_path
