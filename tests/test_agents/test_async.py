"""Tests for async agent support (BaseAgent.arun, Orchestrator.agenerate)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestBaseAgentAsync:
    """Test BaseAgent.arun() async method."""

    def test_arun_exists(self):
        """BaseAgent should have an arun method."""
        from promptbim.agents.base import BaseAgent

        agent = BaseAgent()
        assert hasattr(agent, "arun")
        assert asyncio.iscoroutinefunction(agent.arun)

    def test_async_client_property(self):
        """async_client should create an AsyncAnthropic instance."""
        from promptbim.agents.base import BaseAgent

        agent = BaseAgent()
        # Mock to avoid actual API key requirement
        with patch("anthropic.AsyncAnthropic") as mock_cls:
            agent._settings = MagicMock(anthropic_api_key="sk-ant-test-key-12345678901234567890")
            _ = agent.async_client
            mock_cls.assert_called_once()

    @pytest.mark.asyncio
    async def test_arun_returns_response(self):
        """arun should return AgentResponse on success."""
        from promptbim.agents.base import AgentResponse, BaseAgent

        agent = BaseAgent()

        mock_response = AgentResponse(text="test", usage={"input_tokens": 1, "output_tokens": 1})
        with patch.object(agent, "_async_call_api", new_callable=AsyncMock, return_value=mock_response):
            result = await agent.arun("test prompt")
            assert result.ok
            assert result.text == "test"

    @pytest.mark.asyncio
    async def test_arun_handles_error(self):
        """arun should return error response on failure."""
        from promptbim.agents.base import BaseAgent

        agent = BaseAgent()

        with patch.object(agent, "_async_call_api", new_callable=AsyncMock, side_effect=RuntimeError("fail")):
            result = await agent.arun("test")
            assert not result.ok
            assert "fail" in result.error


class TestEnhancerAsync:
    """Test EnhancerAgent.aenhance()."""

    def test_aenhance_exists(self):
        """EnhancerAgent should have aenhance method."""
        from promptbim.agents.enhancer import EnhancerAgent

        agent = EnhancerAgent()
        assert hasattr(agent, "aenhance")
        assert asyncio.iscoroutinefunction(agent.aenhance)


class TestPlannerAsync:
    """Test PlannerAgent.aplan()."""

    def test_aplan_exists(self):
        """PlannerAgent should have aplan method."""
        from promptbim.agents.planner import PlannerAgent

        agent = PlannerAgent()
        assert hasattr(agent, "aplan")
        assert asyncio.iscoroutinefunction(agent.aplan)


class TestCheckerAsync:
    """Test CheckerAgent.acheck()."""

    def test_acheck_exists(self):
        """CheckerAgent should have acheck method."""
        from promptbim.agents.checker import CheckerAgent

        agent = CheckerAgent()
        assert hasattr(agent, "acheck")
        assert asyncio.iscoroutinefunction(agent.acheck)


class TestOrchestratorAsync:
    """Test Orchestrator.agenerate()."""

    def test_agenerate_exists(self):
        """Orchestrator should have agenerate method."""
        from promptbim.agents.orchestrator import Orchestrator

        orch = Orchestrator()
        assert hasattr(orch, "agenerate")
        assert asyncio.iscoroutinefunction(orch.agenerate)


class TestSyncBackwardCompat:
    """Ensure sync methods still work (backward compatibility)."""

    def test_sync_run_still_exists(self):
        """BaseAgent.run() should still exist."""
        from promptbim.agents.base import BaseAgent

        agent = BaseAgent()
        assert hasattr(agent, "run")
        assert not asyncio.iscoroutinefunction(agent.run)

    def test_sync_generate_still_exists(self):
        """Orchestrator.generate() should still exist."""
        from promptbim.agents.orchestrator import Orchestrator

        orch = Orchestrator()
        assert hasattr(orch, "generate")
        assert not asyncio.iscoroutinefunction(orch.generate)
