import importlib.util
from pathlib import Path


APP_PATH = Path(__file__).resolve().parents[1] / "python-service" / "app.py"
spec = importlib.util.spec_from_file_location("agent_app", APP_PATH)
agent_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_app)


def test_calculator_tool():
    result = agent_app.agent_reply("calculate 12 * 8 + 4")
    assert result["source"] == "tool:calculator"
    assert "100" in result["reply"]


def test_planner_tool():
    result = agent_app.agent_reply("make a plan for studying")
    assert result["source"] == "tool:planner"
    assert "1." in result["reply"]


def test_memory_tool_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(agent_app, "MEMORY_FILE", tmp_path / "memory.json")
    saved = agent_app.agent_reply("remember that my test value is green")
    assert saved["source"] == "tool:memory.write"
    recalled = agent_app.agent_reply("what do you remember")
    assert "test value is green" in recalled["reply"]
