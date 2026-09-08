"""
Excel Workbook Generator for JainBiz Lead Miner.
Creates professional, styled Excel workbooks with auto-filters, clickable photo links,
and color-coded verification badges using openpyxl.
"""

import os
from typing import List, Dict, Any
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generate_leads_excel(records: List[Dict[str, Any]], output_path: str, category: str = "", scope: str = "") -> str:
    """
    Generates a beautifully styled Excel workbook from lead records.
    """
    wb = Workbook()
    
    # ------------------ SHEET 1: MASTER LEADS ------------------
    ws = wb.active
    ws.title = "Jain Verified Leads"
    
    # Header Styles
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1E1B4B", end_color="1E1B4B", fill_type="solid") # Dark Indigo
    
    # Body Styles
    data_font = Font(name="Segoe UI", size=10, color="1E293B")
    link_font = Font(name="Segoe UI", size=10, color="2563EB", underline="single")
    
    tier_100_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid") # Soft Emerald
    tier_100_font = Font(name="Segoe UI", size=10, bold=True, color="166534")
    
    tier_85_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # Soft Amber
    tier_85_font = Font(name="Segoe UI", size=10, bold=True, color="92400E")
    
    tier_70_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    tier_70_font = Font(name="Segoe UI", size=10, color="475569")
    
    thin_border_side = Side(border_style="thin", color="E2E8F0")
    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    
    headers = [
        "Sl.", "Firm / Business Name", "Verification Status", "Proof / Match Reason",
        "Phone Number", "Address", "City", "State", "Rating & Reviews",
        "Storefront Photo (Click HD)", "Website", "Google Maps URL"
    ]
    
    ws.append(headers)
    
    # Style Headers
    for col_num in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)
        cell.border = cell_border
        
    ws.row_dimensions[1].height = 28
    
    # Populate Rows
    for idx, rec in enumerate(records, start=1):
        row_num = idx + 1
        firm_name = rec.get("name", "N/A")
        tier = rec.get("tier", "⚪ 70% Lead Match")
        reason = rec.get("reason", "Category Correlation")
        phone = rec.get("phone", "Not Listed")
        address = rec.get("address", "N/A")
        city = rec.get("city", "N/A")
        state = rec.get("state", "N/A")
        rating = rec.get("rating", "N/A")
        photo_url = rec.get("photo_url", "")
        website = rec.get("website", "")
        maps_url = rec.get("maps_url", "")
        
        row_values = [
            idx,
            firm_name,
            tier,
            reason,
            phone,
            address,
            city,
            state,
            rating,
            "📸 View Storefront Photo" if photo_url else "No Photo",
            "Visit Website" if website else "",
            "Open Google Map" if maps_url else ""
        ]
        
        ws.append(row_values)
        ws.row_dimensions[row_num].height = 22
        
        # Apply Cells Styling
        for col_idx in range(1, len(row_values) + 1):
            cell = ws.cell(row=row_num, column=col_idx)
            cell.font = data_font
            cell.border = cell_border
            cell.alignment = Alignment(vertical="center")
            
            # Align center for index, phone, rating
            if col_idx in [1, 5, 7, 8, 9]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                
            # Style Verification Status Badge
            if col_idx == 3:
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
                
            # Style Hyperlinks
            if col_idx == 10 and photo_url:
                cell.hyperlink = photo_url
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 11 and website:
                cell.hyperlink = website
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 12 and maps_url:
                cell.hyperlink = maps_url
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

    # Auto-adjust column widths
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
        
    ws.column_dimensions["A"].width = 7   # Sl.
    ws.column_dimensions["B"].width = 30  # Firm Name
    ws.column_dimensions["D"].width = 28  # Reason
    ws.column_dimensions["F"].width = 38  # Address
    
    # Enable AutoFilter
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{len(records) + 1}"

    # ------------------ SHEET 2: SUMMARY & STATS ------------------
    ws_summary = wb.create_sheet(title="Executive Summary")
    ws_summary.append(["JainBiz Mining Execution Summary"])
    ws_summary["A1"].font = Font(name="Segoe UI", size=14, bold=True, color="1E1B4B")
    
    total_firms = len(records)
    verified_100 = sum(1 for r in records if "100%" in r.get("tier", ""))
    high_85 = sum(1 for r in records if "85%" in r.get("tier", ""))
    with_phones = sum(1 for r in records if r.get("phone") and r.get("phone") != "Not Listed")
    with_photos = sum(1 for r in records if r.get("photo_url"))
    
    metrics = [
        ["Target Category", category or "All Commercial"],
        ["Geographic Scope", scope or "Pan India"],
        ["Total Firms Discovered", total_firms],
        ["🟢 100% Confirmed Jain Firms", verified_100],
        ["🟡 85% High Match (Surname/Cluster)", high_85],
        ["Active Phone Numbers Verified", with_phones],
        ["Storefront Photos Attached", with_photos]
    ]
    
    ws_summary.append([])
    for metric in metrics:
        ws_summary.append(metric)
        
    for row in ws_summary.iter_rows(min_row=3, max_row=9, min_col=1, max_col=2):
        for cell in row:
            cell.font = Font(name="Segoe UI", size=11)
            cell.border = cell_border
            if cell.column == 1:
                cell.font = Font(name="Segoe UI", size=11, bold=True, color="334155")
                cell.fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
                
    ws_summary.column_dimensions["A"].width = 35
    ws_summary.column_dimensions["B"].width = 25
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    return output_path
