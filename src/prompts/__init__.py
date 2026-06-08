"""
Prompts Module

Centralized access to all agent prompts.
"""
from .architect import SYSTEM_ARCHITECT_PROMPT
from .threat_identifier import STRIDE_THREAT_IDENTIFIER_PROMPT
from .impact_assessor import IMPACT_ASSESSOR_PROMPT
from .mitigation_advisor import MITIGATION_ADVISOR_PROMPT
from .governance import GOVERNANCE_PROMPT

__all__ = [
    "SYSTEM_ARCHITECT_PROMPT",
    "STRIDE_THREAT_IDENTIFIER_PROMPT",
    "IMPACT_ASSESSOR_PROMPT",
    "MITIGATION_ADVISOR_PROMPT",
    "GOVERNANCE_PROMPT",
]
