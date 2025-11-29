#!/usr/bin/env python3
"""Script to extract election results from PDF and save as JSON"""

import json
import re

import pdfplumber


def extract_constituency_info(text):
    """Extract constituency number, name, and total electors from text"""
    # Pattern: "Constituency: 1 . Araku ( Total Electors 1557153)"
    pattern = r"Constituency:\s*(\d+)\s*\.\s*(.+?)\s*\(\s*Total Electors\s*(\d+)\s*\)"
    match = re.search(pattern, text)
    if match:
        return {
            "constituency_number": int(match.group(1)),
            "constituency_name": match.group(2).strip(),
            "total_electors": int(match.group(3)),
        }
    return None


def parse_table_row(row, headers):
    """Parse a table row into a structured dictionary"""
    if not row or len(row) < 10:
        return None

    # Skip header rows and total rows
    if row[0] is None or str(row[0]).strip().upper() in ["SL", "SL NO", "TOTAL", ""]:
        return None

    try:
        candidate = {
            "serial_number": (
                int(row[0]) if row[0] and str(row[0]).strip().isdigit() else None
            ),
            "candidate_name": str(row[1]).strip().replace("\n", " ") if row[1] else "",
            "gender": str(row[2]).strip() if row[2] else "",
            "age": int(row[3]) if row[3] and str(row[3]).strip().isdigit() else None,
            "category": str(row[4]).strip() if row[4] else "",
            "party": str(row[5]).strip() if row[5] else "",
            "symbol": str(row[6]).strip().replace("\n", " ") if row[6] else "",
            "total_votes_polled": (
                int(row[7])
                if row[7] and str(row[7]).strip().replace(",", "").isdigit()
                else None
            ),
            "valid_votes": (
                int(row[8])
                if row[8] and str(row[8]).strip().replace(",", "").isdigit()
                else None
            ),
            "votes_secured": {
                "general": (
                    int(row[9])
                    if row[9] and str(row[9]).strip().replace(",", "").isdigit()
                    else 0
                ),
                "postal": (
                    int(row[10])
                    if row[10] and str(row[10]).strip().replace(",", "").isdigit()
                    else 0
                ),
                "total": (
                    int(row[11])
                    if row[11] and str(row[11]).strip().replace(",", "").isdigit()
                    else 0
                ),
            },
            "percentage_of_votes": {
                "over_total_electors": (
                    float(row[12])
                    if row[12]
                    and str(row[12])
                    .strip()
                    .replace(",", "")
                    .replace("%", "")
                    .replace("-", "")
                    .strip()
                    else None
                ),
                "over_total_votes_polled": (
                    float(row[13])
                    if row[13]
                    and str(row[13])
                    .strip()
                    .replace(",", "")
                    .replace("%", "")
                    .replace("-", "")
                    .strip()
                    else None
                ),
                "over_total_valid_votes": (
                    float(row[14])
                    if len(row) > 14
                    and row[14]
                    and str(row[14])
                    .strip()
                    .replace(",", "")
                    .replace("%", "")
                    .replace("-", "")
                    .strip()
                    else None
                ),
            },
        }
        return candidate
    except (ValueError, IndexError) as e:
        return None


def extract_pdf_to_json(pdf_path, output_path):
    """Extract all data from PDF and save as JSON"""
    results = {
        "election": "2024 Lok Sabha Elections",
        "state": "Andhra Pradesh",
        "constituencies": [],
    }

    with pdfplumber.open(pdf_path) as pdf:
        current_constituency = None

        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            # Try to extract constituency info
            constituency_info = extract_constituency_info(text)
            if constituency_info:
                # Save previous constituency if exists
                if current_constituency:
                    results["constituencies"].append(current_constituency)

                # Start new constituency
                current_constituency = {
                    "constituency_number": constituency_info["constituency_number"],
                    "constituency_name": constituency_info["constituency_name"],
                    "total_electors": constituency_info["total_electors"],
                    "candidates": [],
                }

            # Extract tables
            tables = page.extract_tables()
            if tables and current_constituency:
                for table in tables:
                    if not table or len(table) < 2:
                        continue

                    # Skip header rows (first 2 rows are usually headers)
                    for row in table[2:]:
                        candidate = parse_table_row(row, None)
                        if candidate and candidate["serial_number"] is not None:
                            # Check if candidate already exists (avoid duplicates)
                            existing = next(
                                (
                                    c
                                    for c in current_constituency["candidates"]
                                    if c["serial_number"] == candidate["serial_number"]
                                ),
                                None,
                            )
                            if not existing:
                                current_constituency["candidates"].append(candidate)

        # Add last constituency
        if current_constituency:
            results["constituencies"].append(current_constituency)

    # Save to JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Extracted data for {len(results['constituencies'])} constituencies")
    print(
        f"Total candidates: {sum(len(c['candidates']) for c in results['constituencies'])}"
    )
    print(f"Saved to: {output_path}")

    return results


if __name__ == "__main__":
    pdf_path = "data/33-Constituency-Wise-Detailed-Result.pdf"
    output_path = "election_results.json"

    try:
        results = extract_pdf_to_json(pdf_path, output_path)
        print("\nExtraction completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
