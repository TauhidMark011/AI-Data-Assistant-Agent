#Phase 3.8: Dynamic Output Parsing Layer
#The AgentOutputParser has now been upgraded with robust regex patterns and flexible multi-pattern support to adapt to variations in the LLM's response format.
#Dynamically extract malformed and missing columns
#Identify and categorize auto/suggested/blocked fixes
#Detect structured null issues (e.g., "Column 'X' has 3 missing values")
#Flexibly capture safe corrective actions using multiple bullet/line styles
#Handle evolving phrasing from the LLM with resilient patterns

import re
from typing import Dict, List

class AgentOutputParser:
    def parse(self, text: str) -> Dict:
        parsed = {
            "null_issues": {},
            "malformed_columns": [],
            "auto_fixes": [],
            "suggested_fixes": [],
            "blocked_fixes": [],
            "nlg_messages": [],
            "raw_agent_output": text.strip()
        }

        # Pattern: Missing required columns
        missing_match = re.search(r"Missing required columns: ?(?:\{|\[)?([^}\]\n]+)(?:\}|\])?", text)
        if missing_match:
            cols = re.split(r"[,\n]", missing_match.group(1))
            parsed["malformed_columns"].extend([c.strip(" '⟨⟩\"“") for c in cols if c.strip()])

        # Pattern: Unexpected or malformed columns
        malformed_match = re.findall(r"Unexpected column detected: ([^\n]+)", text)
        for match in malformed_match:
            cols = re.split(r"[,\n]", match)
            parsed["malformed_columns"].extend([col.strip(" '⟨⟩\"“") for col in cols if col.strip()])

        # Pattern: Column-specific nulls (e.g., "Column 'Votes' has 3 missing values")
        null_line_matches = re.findall(r"Column ['\"]?(\w[\w\s]+)['\"]? has (\d+) missing", text)
        for col, count in null_line_matches:
            parsed["null_issues"][col.strip()] = int(count)

        # Pattern: High % of null values dict
        nulls_match = re.search(r"High % of null values:\s*\{([^}]+)\}", text)
        if nulls_match:
            entries = nulls_match.group(1).split(",")
            for entry in entries:
                parts = entry.strip().split(":")
                if len(parts) == 2:
                    col = parts[0].strip(" '\"")
                    try:
                        val = float(parts[1])
                        parsed["null_issues"][col] = round(val, 2)
                    except:
                        continue

        #NEW: Detect float null value phrasing (e.g., "'Location': The detected null value (32.65)...")
        #Alternative phrasing for null % detection (e.g., "null value (3.33)")
        null_value_matches = re.findall(r"'([^']+)':.*?null value\s*\(([\d.]+)\)", text, re.IGNORECASE)
        for col, pct in null_value_matches:
            try:
                parsed["null_issues"][col.strip()] = round(float(pct), 2)
            except:
                continue

        #NEW: Detect column type mismatches (e.g., "'Item': may contain float values instead of string")
#Add detection for schema violations due to wrong types and populate under "malformed_columns" or a new "type_issues" field.
        type_mismatch_lines = re.findall(
            r"'([^']+)':.*?may contain .*? instead of (\w+)", text, re.IGNORECASE)
        for col, expected_type in type_mismatch_lines:
            parsed["malformed_columns"].append(
                f"{col.strip()} (violates expected type: {expected_type.strip()})")

        # Fix categories
        fix_patterns = {
            "auto_fixes": r"\bAuto[- ]?fix applied: ([^\n]+)",
            "suggested_fixes": r"\bSuggested fix: ([^\n]+)",
            "blocked_fixes": r"\bFix blocked: ([^\n]+)"
        }
        for field, pattern in fix_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            parsed[field].extend([m.strip() for m in matches])

        # NLG block
        corrective_block = re.split(r"(?i)safe corrective actions.*?:", text)
        if len(corrective_block) > 1:
            lines = corrective_block[1].split("\n")
            for line in lines:
                cleaned = line.strip(" -•:\n\t")
                if cleaned and len(cleaned) > 3:
                    parsed["nlg_messages"].append(cleaned)

        return parsed
