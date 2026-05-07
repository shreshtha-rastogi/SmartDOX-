def generate_explanation(criteria, bidder, results):
    explanation = {}

    # Turnover
    explanation["turnover"] = {
        "status": results["turnover"],
        "required": f">= {criteria['turnover']} crore",
        "found": f"{bidder['turnover']} crore" if bidder["turnover"] else "Not Found",
        "reason": get_reason("turnover", results["turnover"])
    }

    # Projects
    explanation["projects"] = {
        "status": results["projects"],
        "required": f">= {criteria['projects']} projects",
        "found": f"{bidder['projects']} projects" if bidder["projects"] else "Not Found",
        "reason": get_reason("projects", results["projects"])
    }

    # GST
    explanation["gst"] = {
        "status": results["gst"],
        "required": "GST Registration Required",
        "found": "Available" if bidder["gst"] else "Not Found",
        "reason": get_reason("gst", results["gst"])
    }

    # ISO
    explanation["iso"] = {
        "status": results["iso"],
        "required": "ISO Certification Required",
        "found": "Available" if bidder["iso"] else "Not Found",
        "reason": get_reason("iso", results["iso"])
    }

    return explanation


def get_reason(field, status):
    if status == "PASS":
        return f"{field} requirement satisfied"
    elif status == "FAIL":
        return f"{field} requirement not met"
    else:
        return f"{field} data unclear, needs review"