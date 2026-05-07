def evaluate(criteria, bidder):
    result = {}

    # Turnover check
    if bidder["turnover"] is None:
        result["turnover"] = "REVIEW"
    elif bidder["turnover"] >= criteria["turnover"]:
        result["turnover"] = "PASS"
    else:
        result["turnover"] = "FAIL"

    # Projects check
    if bidder["projects"] is None:
        result["projects"] = "REVIEW"
    elif bidder["projects"] >= criteria["projects"]:
        result["projects"] = "PASS"
    else:
        result["projects"] = "FAIL"

    # GST check
    result["gst"] = "PASS" if bidder["gst"] else "FAIL"

    # ISO check
    result["iso"] = "PASS" if bidder["iso"] else "FAIL"

    return result


def final_verdict(results):
    if "FAIL" in results.values():
        return "Not Eligible"
    elif "REVIEW" in results.values():
        return "Needs Manual Review"
    else:
        return "Eligible"