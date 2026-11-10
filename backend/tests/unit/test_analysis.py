import pytest
from app.services.analysis_service import AnalysisService


def test_circular_dependency_detection():
    # A -> B -> C -> A (cycle)
    dep_graph = {
        "mod_a.py": ["mod_b"],
        "mod_b.py": ["mod_c"],
        "mod_c.py": ["mod_a"],
        "mod_d.py": ["mod_a"],
    }
    sccs = AnalysisService.detect_circular_dependencies(dep_graph)
    assert len(sccs) == 1
    cycle = sccs[0]
    assert len(cycle) == 3
    assert set(cycle) == {"mod_a", "mod_b", "mod_c"}


def test_framework_detection(tmp_path):
    # Create fake package.json and requirements.txt
    pkg_json = tmp_path / "package.json"
    pkg_json.write_text('{"dependencies": {"next": "15.0.0", "react": "19.0.0"}}', encoding="utf-8")

    reqs = tmp_path / "requirements.txt"
    reqs.write_text("fastapi==0.115.0\nlanggraph>=0.2.0", encoding="utf-8")

    frameworks = AnalysisService.detect_frameworks(tmp_path)
    assert "Next.js" in frameworks
    assert "React" in frameworks
    assert "FastAPI" in frameworks
    assert "LangGraph" in frameworks
