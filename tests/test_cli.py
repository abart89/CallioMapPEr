import csv
from pathlib import Path
from calliomapper.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_template_real_file_no_overwrite(tmp_path):
    path = tmp_path / 'annotations.yaml'
    assert main(['init-annotations','--out',str(path)]) == 0
    assert 'schema_version: 1' in path.read_text()
    assert main(['init-annotations','--out',str(path)]) == 1


def test_translate_query_and_error_status(tmp_path):
    graph = tmp_path / 'national.nq'
    output = tmp_path / 'answer.csv'
    assert main(['translate',str(ROOT / 'examples/national_scale/results_directory'), '--out',str(graph), '--groups','capacities']) == 0
    assert main(['query',str(graph),'--preset','installed_capacity','--out',str(output)]) == 0
    with output.open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 15
    assert main(['translate',str(tmp_path / 'absent'),'--out',str(graph)]) == 1
    assert main(['query',str(graph),'--preset','unknown']) == 1
