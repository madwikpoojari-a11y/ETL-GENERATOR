"""
healing_agent.py  —  Agent Layer
-----------------------------------
Orchestrates all self-healing rules. Receives the raw DataFrame and
validation results, evaluates each rule in order, applies triggered rules,
and returns the healed DataFrame plus a full healing log.

Rule evaluation order matters:
  1. Missing columns must be fixed before type/null checks
  2. Duplicates before null imputation (fewer rows = faster imputation)
  3. Date format before type coercion
  4. Type mismatch before null handling (coercion may introduce new nulls)
  5. High nulls last (catches nulls from all previous steps)
"""

import pandas as pd
from datetime import datetime
from src.utils.logger import get_logger

from src.agent.rules import (
    rule_missing_column,
    rule_duplicates,
    rule_date_format,
    rule_type_mismatch,
    rule_high_nulls,
)

logger = get_logger(__name__)

# Ordered list of (rule_module, rule_name) tuples
RULES = [
    (rule_missing_column, "Missing Column Detection"),
    (rule_duplicates,     "Duplicate Explosion"),
    (rule_date_format,    "Date Format Normalization"),
    (rule_type_mismatch,  "Datatype Mismatch"),
    (rule_high_nulls,     "High Null Percentage"),
]


def heal(df: pd.DataFrame, validation_results: dict) -> tuple[pd.DataFrame, list]:
    """
    Evaluates and applies all self-healing rules in sequence.

    Input:
        df                 — DataFrame after ingestion and initial validation
        validation_results — dict produced by running all validators
                             (passed as context to each rule)

    Output:
        healed_df    — DataFrame after all triggered rules have been applied
        healing_log  — list of dicts, one per triggered rule action
    """
    logger.info("Self-Healing Agent started.")
    healing_log = []
    context = validation_results  # rules may read validation metadata

    for rule_module, rule_name in RULES:
        try:
            triggered = rule_module.evaluate(df, context)
            if triggered:
                logger.info("Rule TRIGGERED: %s", rule_name)
                df, actions = rule_module.apply(df, context)

                for action in actions:
                    action["rule_name"]    = rule_name
                    action["triggered_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    healing_log.append(action)
                    logger.info(
                        "[%s] %s → %s (%s)",
                        action["rule_id"],
                        action["trigger"],
                        action["action"],
                        action["outcome"],
                    )
            else:
                logger.info("Rule SKIPPED (not triggered): %s", rule_name)

        except Exception as e:
            logger.error("Rule '%s' raised an exception: %s", rule_name, str(e))
            healing_log.append({
                "rule_id":     "UNKNOWN",
                "rule_name":   rule_name,
                "trigger":     "Exception during rule evaluation",
                "action":      "Rule aborted",
                "outcome":     "ERROR",
                "column":      "N/A",
                "triggered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error":       str(e),
            })

    rules_triggered = sum(1 for a in healing_log if a.get("outcome") != "ERROR")
    logger.info(
        "Self-Healing Agent complete. %d rule(s) triggered, %d action(s) logged.",
        rules_triggered, len(healing_log)
    )

    return df, healing_log


def get_healing_summary(healing_log: list) -> pd.DataFrame:
    """
    Converts the healing log list to a display-ready DataFrame.

    Output columns: rule_id, rule_name, trigger, action, outcome,
                    column, triggered_at
    """
    if not healing_log:
        return pd.DataFrame(columns=[
            "rule_id", "rule_name", "trigger", "action",
            "outcome", "column", "triggered_at"
        ])

    rows = []
    for entry in healing_log:
        rows.append({
            "rule_id":      entry.get("rule_id", ""),
            "rule_name":    entry.get("rule_name", ""),
            "trigger":      entry.get("trigger", ""),
            "action":       entry.get("action", ""),
            "outcome":      entry.get("outcome", ""),
            "column":       entry.get("column", ""),
            "triggered_at": entry.get("triggered_at", ""),
        })

    return pd.DataFrame(rows)
