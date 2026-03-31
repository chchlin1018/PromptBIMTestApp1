"""AI/LLM layer for natural language → bim_core operations.

Provides NLParser, IntentRouter, ConversationHistory, and ErrorHandler
to bridge natural language commands to C++ BIM scene actions.
"""

from promptbim.ai.nl_parser import NLParser, BIMIntent
from promptbim.ai.intent_router import IntentRouter
from promptbim.ai.conversation_history import ConversationHistory
from promptbim.ai.error_handler import ErrorHandler

__all__ = ["NLParser", "BIMIntent", "IntentRouter", "ConversationHistory", "ErrorHandler"]
