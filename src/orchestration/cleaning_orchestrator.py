#orchestration/ → decision authority
"""
cleaning_orchestrator.py

Phase 3.6:
Central decision engine that orchestrates all cleaning actions.

Responsibilities:
- Aggregate actions from all cleaning tools
- Assign decisions based on confidence
- Resolve conflicts
- Produce final, auditable cleaning plan
"""

from typing import List, Dict

#confidence ≥ 0.90  → AUTO_APPLY
#0.75 ≤ confidence < 0.90 → SUGGEST
#confidence < 0.75 → BLOCK
class CleaningOrchestrator:
    def __init__(
        self,
        auto_threshold: float = 0.90,
        suggest_threshold: float = 0.75
    ):
        """
        Thresholds define agent autonomy boundaries.
        """
        self.auto_threshold = auto_threshold
        self.suggest_threshold = suggest_threshold

    def decide(self, actions: List[Dict]) -> Dict:
        """
        Core decision logic.

        Input:
        - actions: list of action dictionaries from all tools

        Output:
        - structured cleaning plan
        """

        applied = []
        suggested = []
        blocked = []

        for action in actions:
            confidence = action.get("confidence", 0.0)

            # High confidence → safe to auto-apply
            if confidence >= self.auto_threshold:
                action["decision"] = "AUTO_APPLY"
                applied.append(action)

            # Medium confidence → suggest only
            elif confidence >= self.suggest_threshold:
                action["decision"] = "SUGGEST"
                suggested.append(action)

            # Low confidence → block
            else:
                action["decision"] = "BLOCK"
                blocked.append(action)

        return {
            "applied_fixes": applied,
            "suggested_fixes": suggested,
            "blocked_fixes": blocked,
            "summary": {
                "applied": len(applied),
                "suggested": len(suggested),
                "blocked": len(blocked)
            }
        }
