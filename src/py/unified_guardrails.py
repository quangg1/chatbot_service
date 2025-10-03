"""
Unified Guardrails: combines NeMo Guardrails config (config.yml + flows.co)
with custom MedicalGuardrails logic into a single interface for input/output validation
and optional intent detection bridges.

Public API:
- UnifiedGuardrails.validate_input(user_input) -> dict
- UnifiedGuardrails.validate_output(response, is_medical=True) -> str
- UnifiedGuardrails.detect_intent(query) -> str

This class internally initializes NeMo LLMRails when available, and delegates
to MedicalGuardrails for Vietnamese-focused safety and tone. It ensures a single
instance can be reused by both CLI and Streamlit UI to avoid duplication.
"""

from __future__ import annotations

from typing import Dict, Any, Optional
import os
from pathlib import Path

try:
    from nemoguardrails import RailsConfig, LLMRails
except Exception:
    RailsConfig = None
    LLMRails = None

from medical_guardrails import MedicalGuardrails


class UnifiedGuardrails:
    def __init__(self, llm=None, config_path: str = ".") -> None:
        self.medical = MedicalGuardrails()
        self.rails = None
        self.rails_active: bool = False
        # Resolve config path to this file's directory by default
        base_dir = Path(config_path)
        if not base_dir.exists() or base_dir.is_file():
            base_dir = Path(__file__).parent
        try:
            if RailsConfig is not None and LLMRails is not None:
                cfg = RailsConfig.from_path(str(base_dir))
                self.rails = LLMRails(cfg, llm=llm) if llm is not None else LLMRails(cfg)
                self.rails_active = True
        except Exception:
            self.rails = None
            self.rails_active = False

    # Input validation delegates to MedicalGuardrails (VN-first)
    def validate_input(self, user_input: str) -> Dict[str, Any]:
        # Primary validation via MedicalGuardrails
        result = self.medical.validate_input(user_input)
        # Optional: If NeMo rails are active, we could run input flows here in the future.
        # Current flows are mirrored by MedicalGuardrails, so we avoid duplicate work.
        return result

    # Output validation delegates to MedicalGuardrails; NeMo flows are loaded
    # and can be leveraged in future for post-processing if needed.
    def validate_output(self, response: str, is_medical: bool = True) -> str:
        # Primary post-processing via MedicalGuardrails (adds disclaimer, trims, safety)
        processed = self.medical.validate_output(response, is_medical=is_medical)
        # Optional: place to apply additional NeMo-based checks/rewrites if needed.
        return processed

    # Intent detection keeps current behavior via MedicalGuardrails
    def detect_intent(self, query: str) -> str:
        return self.medical.detect_intent(query)

    # Entity extraction bridge
    def extract_entities(self, text: str) -> Dict[str, Any]:
        return self.medical.extract_entities(text)

    # Expose underlying rails for advanced usage (optional by caller)
    def get_rails(self):
        return self.rails

    # Convenience check
    def is_rails_active(self) -> bool:
        return bool(self.rails_active and self.rails is not None)

    # Optional helper: run a named NeMo flow if available; no-op fallback
    def run_flow(self, flow_name: str, user_input: Optional[str] = None) -> Optional[str]:
        """
        Attempt to run a NeMo Guardrails flow by name. Returns a response string
        if the flow yields a bot message; otherwise returns None. This is
        intentionally conservative to avoid duplicating logic handled by
        MedicalGuardrails.
        """
        try:
            if not self.is_rails_active():
                return None
            rails = self.rails
            # Some flows are output-only checks; others react to user input.
            # If user_input provided, we pass it to converse; otherwise try a flow trigger.
            if user_input is not None:
                conv = rails.converse(user_input)
                # conv is a generator; collect first bot message
                for msg in conv:
                    if isinstance(msg, str) and msg.strip():
                        return msg
                return None
            else:
                # Direct flow execution if supported in current rails version
                if hasattr(rails, "run_flow"):
                    out = rails.run_flow(flow_name)
                    if isinstance(out, str) and out.strip():
                        return out
                return None
        except Exception:
            return None


