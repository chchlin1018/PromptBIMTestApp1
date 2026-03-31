# S-PTB-AI-LAYER PROMPT v1.0 — AI/LLM 語義解析→bim_core [15T/3P]

Sprint: S-PTB-AI-LAYER | 專案: PTB | 機器: Mac Mini
目標: mvp-v0.9.0-ai | 規格: 15T/3P | ⛔ pytest 禁止

## P1/3: AI 層實作 (7T)
- T01: NLParser class
- T02: Claude API client
- T03: IntentRouter
- T04: 13 actions 全部接通
- T05: ConversationHistory
- T06: ErrorHandler
- T07: ChatPanel 整合

## P2/3: 驗證 (4T)
- T08: ctest ALL PASS
- T09: python -c 驗證 NLParser
- T10: python -c 驗證 Claude API (mock)
- T11: 端到端驗證

## P3/3: Finalize (4T)
- T12: cmake --build + ctest
- T13: AuditReport
- T14: git tag mvp-v0.9.0-ai
- T15: 完成通知
