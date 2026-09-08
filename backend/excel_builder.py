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
    
    # Live Sync Portal Styles (Cols 24-26)
    portal_header_fill = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid") # Deep Emerald
    portal_header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    
    status_ready_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # Amber
    status_ready_font = Font(name="Segoe UI", size=9, bold=True, color="92400E")
    status_done_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid") # Emerald
    status_done_font = Font(name="Segoe UI", size=9, bold=True, color="166534")
    status_fail_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid") # Red
    status_fail_font = Font(name="Segoe UI", size=9, bold=True, color="991B1B")
    
    biz_id_font = Font(name="Segoe UI", size=9, bold=True, color="065F46")
    coord_font = Font(name="Segoe UI", size=9, color="047857")
    
    thin_border_side = Side(border_style="thin", color="E2E8F0")
    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    
    # 26 Optimized Columns matching JainForJain's 4-Tab Form & Bot Auto-Sync
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
        "District",
        "State",
        "Pincode",
        "Latitude",
        "Longitude",
        "Google Maps URL",
        "Website URL",
        "Storefront Signboard (1600px HD)",
        "Showroom / Products (1600px HD)",
        "All Photos Gallery (Google Maps)",
        "Official Website Logo",
        "Auto-Generated Description (Ready to Paste)",
        "Verification Status",
        "Proof / Match Reason",
        "JainForJain Business ID",
        "JainForJain Live Profile URL",
        "Submission Status"
    ]
    
    ws.append(headers)
    
    # Style Headers
    for col_num in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_num)
        if col_num >= 24: # JainForJain Sync Columns
            cell.font = portal_header_font
            cell.fill = portal_header_fill
        else:
            cell.font = header_font
            cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = cell_border
        
    ws.row_dimensions[1].height = 36
    
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
        district = rec.get("district") or city
        state = rec.get("state", "N/A")
        pincode = rec.get("pincode", "N/A")
        
        latitude = rec.get("latitude", "")
        longitude = rec.get("longitude", "")
        
        maps_url = rec.get("maps_url", "")
        website = rec.get("website", "")
        
        storefront_photo = rec.get("storefront_photo") or rec.get("photo_url", "")
        showcase_photo = rec.get("showcase_photo", "")
        gallery_url = rec.get("gallery_url") or maps_url
        web_logo = rec.get("website_logo", "")
        
        desc = rec.get("description", "")
        tier = rec.get("tier", "⚪ 70% Lead Match")
        reason = rec.get("reason", "Category Correlation")
        
        biz_id = rec.get("j4j_business_id", "")
        profile_url = rec.get("j4j_profile_url", "")
        submission_status = rec.get("submission_status", "Ready to Submit")
        
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
            district,
            state,
            pincode,
            latitude,
            longitude,
            "Open Google Map" if maps_url else "",
            "Visit Website" if website else "",
            "📸 View Storefront (1600px)" if storefront_photo else "No Photo Listed",
            "🏬 View Showroom (1600px)" if showcase_photo else "Check Gallery",
            "🌐 Browse All Photos" if gallery_url else "",
            "🏷️ View Web Logo" if web_logo else "Use Storefront Photo",
            desc,
            tier,
            reason,
            biz_id,
            "🔗 View Live Profile" if profile_url else "",
            submission_status
        ]
        
        ws.append(row_values)
        ws.row_dimensions[row_num].height = 45 # Comfortable view for multi-line description preview
        
        # Apply Cells Styling
        for col_idx in range(1, len(row_values) + 1):
            cell = ws.cell(row=row_num, column=col_idx)
            cell.font = data_font
            cell.border = cell_border
            cell.alignment = Alignment(vertical="center")
            
            # Align center for index, phone, whatsapp, city, district, state, pincode, lat, lng
            if col_idx in [1, 5, 6, 9, 10, 11, 12, 13, 14]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                
            # Style Latitude & Longitude (Cols 13, 14)
            if col_idx in [13, 14]:
                cell.font = coord_font
                
            # Style Category column (Col 3)
            if col_idx == 3:
                cell.font = cat_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Style Owner column (Col 4)
            if col_idx == 4:
                cell.font = owner_font

            # Style Hyperlinks
            if col_idx == 15 and maps_url:
                cell.hyperlink = maps_url
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 16 and website:
                cell.hyperlink = website
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 17 and storefront_photo:
                cell.hyperlink = storefront_photo
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 18 and showcase_photo:
                cell.hyperlink = showcase_photo
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 19 and gallery_url:
                cell.hyperlink = gallery_url
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 20 and web_logo:
                cell.hyperlink = web_logo
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Style Description column (Col 21)
            if col_idx == 21:
                cell.font = desc_font
                cell.alignment = Alignment(vertical="top", wrap_text=True)

            # Style Verification Status Badge (Col 22)
            if col_idx == 22:
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

            # Style JainForJain Business ID (Col 24)
            if col_idx == 24:
                cell.font = biz_id_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
                
            # Style JainForJain Profile Link (Col 25)
            if col_idx == 25 and profile_url:
                cell.hyperlink = profile_url
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
                
            # Style Submission Status Badge (Col 26)
            if col_idx == 26:
                if "Submitted" in submission_status or "Live" in submission_status or "Approved" in submission_status:
                    cell.fill = status_done_fill
                    cell.font = status_done_font
                elif "Error" in submission_status or "Failed" in submission_status:
                    cell.fill = status_fail_fill
                    cell.font = status_fail_font
                else:
                    cell.fill = status_ready_fill
                    cell.font = status_ready_font
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
        "J": 16,  # District
        "K": 16,  # State
        "L": 12,  # Pincode
        "M": 14,  # Latitude
        "N": 14,  # Longitude
        "O": 18,  # Maps Link
        "P": 18,  # Website
        "Q": 26,  # Storefront Photo Link
        "R": 26,  # Showroom Photo Link
        "S": 24,  # Google Photos Gallery Link
        "T": 24,  # Official Web Logo Link
        "U": 55,  # Description
        "V": 20,  # Verification Status
        "W": 26,  # Proof Reason
        "X": 22,  # JainForJain Business ID
        "Y": 24,  # JainForJain Live Profile URL
        "Z": 18   # Submission Status
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
    with_storefront = sum(1 for r in records if r.get("storefront_photo"))
    with_showcase = sum(1 for r in records if r.get("showcase_photo"))
    with_web_logo = sum(1 for r in records if r.get("website_logo"))
    
    metrics = [
        ["Target Category", category or "All Commercial"],
        ["Geographic Scope", scope or "Pan India"],
        ["Total Leads Extracted", total_firms],
        ["🟢 100% Confirmed Jain Firms", verified_100],
        ["🟡 85% High Match (Surname/Cluster)", high_85],
        ["Active Calling & WhatsApp Numbers", with_phones],
        ["Extracted 6-Digit Postal Pincodes", with_pincodes],
        ["Authentic 1600px Storefront Photos", with_storefront],
        ["Authentic 1600px Showroom / Products Photos", with_showcase],
        ["Verified Custom Website Logos", with_web_logo],
        ["Synthesized Ready-to-Paste Descriptions", total_firms]
    ]
    
    ws_summary.append([])
    for metric in metrics:
        ws_summary.append(metric)
        
    for row in ws_summary.iter_rows(min_row=3, max_row=12, min_col=1, max_col=2):
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
