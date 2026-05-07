import re

# -------------------------------
# 1. Extract Criteria from Tender
# -------------------------------
def extract_criteria(text):
    text = text.lower()
    criteria = {}

    # Turnover (e.g., "5 crore")
    turnover_match = re.search(r'(\d+)\s*crore', text)
    if turnover_match:
        criteria["turnover"] = int(turnover_match.group(1))
    else:
        criteria["turnover"] = None

    # Projects (e.g., "3 projects")
    project_match = re.search(r'(\d+)\s*(projects|project)', text)
    if project_match:
        criteria["projects"] = int(project_match.group(1))
    else:
        criteria["projects"] = None

    # GST (keyword presence)
    criteria["gst"] = "gst" in text

    # ISO (keyword presence)
    criteria["iso"] = "iso" in text

    return criteria


# -----------------------------------
# 2. Extract Data from Bidder Document
# -----------------------------------
def extract_bidder_data(text):
    text = text.lower()
    data = {}

    # Turnover
    turnover_match = re.search(r'(\d+)\s*crore', text)
    if turnover_match:
        data["turnover"] = int(turnover_match.group(1))
    else:
        data["turnover"] = None

    # Projects
    project_match = re.search(r'(\d+)\s*(projects|project)', text)
    if project_match:
        data["projects"] = int(project_match.group(1))
    else:
        data["projects"] = None

    # GST
    data["gst"] = "gst" in text

    # ISO
    data["iso"] = "iso" in text

    return data