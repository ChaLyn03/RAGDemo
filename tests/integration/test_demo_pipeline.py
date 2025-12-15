from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from nxrag.pipeline.run import run_pipeline


def test_demo_pipeline_produces_markdown(tmp_path):
    sample_input = Path("assets/samples/nx_code/widget_housing_request.txt")
    output_path = run_pipeline(sample_input, Path("configs/app.yaml"))

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")

    assert "Part description: Widget housing" in content
    assert "6061-T6 aluminum" in content
    assert "threadlocker" in content
