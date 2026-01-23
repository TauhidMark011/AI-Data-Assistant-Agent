#Phase 3.7: OUTPUT REPORT STRUCTURE UPDATE
from typing import List, Dict, Union

def generate_structured_report(
    null_issues: Dict[str, int],
    malformed_columns: List[str],
    auto_fixes: List[str],
    suggested_fixes: List[str],
    blocked_fixes: List[str],
    nlg_messages: List[str],
    return_format: str = "string"  # "dict" or "string"
) -> Union[str, dict]:
    report_dict = {
        "null_issues": null_issues,
        "malformed_columns": malformed_columns,
        "auto_fixes": auto_fixes,
        "suggested_fixes": suggested_fixes,
        "blocked_fixes": blocked_fixes,
        "natural_language_summary": nlg_messages
    }

    if return_format == "dict":
        return report_dict

    # Default is human-readable text report
    report = []
    report.append("=== DATA QUALITY REPORT (Structured) ===")

    if null_issues and isinstance(null_issues, dict):
        report.append("1. Null Values Detected:")
        for col, count in null_issues.items():
            report.append(f"   - Column '{col}' has {count} null entries.")
        report.append("")

    if malformed_columns and isinstance(malformed_columns, list):
        report.append("2. Malformed/Unexpected Columns:")
        for col in malformed_columns:
            report.append(f"   - Unexpected or malformed column: '{col}'")
        report.append("")

    if auto_fixes or suggested_fixes or blocked_fixes:
        report.append("3. Semantic Typo & Fix Recommendations:")
        if auto_fixes:
            report.append("Auto-Applied Fixes:")
            for fix in auto_fixes:
                report.append(f"     - {fix}")
        if suggested_fixes:
            report.append("Suggested Fixes (Review Required):")
            for fix in suggested_fixes:
                report.append(f"     - {fix}")
        if blocked_fixes:
            report.append("Blocked Fixes (Low Confidence):")
            for fix in blocked_fixes:
                report.append(f"     - {fix}")
        report.append("")

    if nlg_messages and isinstance(nlg_messages, list):
        report.append("4. Summary (Natural Language Insight):")
        for msg in nlg_messages:
            report.append(f"   - {msg}")

    #Ensure something gets printed if all fields are empty
    if not any([null_issues, malformed_columns, auto_fixes, suggested_fixes, blocked_fixes, nlg_messages]):
        return ["=== DATA QUALITY REPORT (Structured) ===", "!!No structured issues were detected or extracted from the LLM response."]
    
    # if len(report) == 1:
    #     report.append("!!No structured issues were detected or extracted from the LLM response. Check parsing logic.")

    print("....Received or not structured report....!")
    print(report)  # debug
    #return "\n".join(report)
    return report

#Example stub test to confirm format
# if __name__ == "__main__":
#     null_issues = {"Votes": 3, "Income": 1, "Unnamed: 8": 24}
#     malformed_columns = ["Original titlÊ", "Genrë¨", "Unnamed: 8"]
#     auto_fixes = ["Genrë¨ → Genre"]
#     suggested_fixes = ["Votes → votes"]
#     blocked_fixes = ["LÃ©on → Léon"]
#     nlg = [
#         "Column 'Votes' contains non-numeric dots. Consider normalization.",
#         "Release year '21-11-46' is ambiguous. ISO format recommended."
#     ]

#     print(generate_structured_report(
#         null_issues,
#         malformed_columns,
#         auto_fixes,
#         suggested_fixes,
#         blocked_fixes,
#         nlg,
#         return_format="string"
#     ))
