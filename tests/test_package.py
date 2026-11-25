from importlib.metadata import entry_points, version
import json


def test_package_installe():
    assert version("logiai") == "0.1.0"


def test_commande_declaree():
    assert "logiai-predict" in {e.name for e in entry_points(group="console_scripts")}


def test_cli_fichier_absent(capsys):
    from logiai.cli import main
    assert main(["fichier_inexistant.json"]) == 1
    assert "introuvable" in capsys.readouterr().err


def test_cli_json_invalide(tmp_path, capsys):
    from logiai.cli import main
    path = tmp_path / "invalide.json"
    path.write_text("{", encoding="utf-8")
    assert main([str(path)]) == 1
    assert "impossible" in capsys.readouterr().err


def test_cli_prediction(tmp_path, monkeypatch, capsys):
    from logiai import cli
    from logiai.api import main as api
    from tests.conftest import VALID
    path = tmp_path / "livraison.json"
    path.write_text(json.dumps(VALID), encoding="utf-8")
    monkeypatch.setattr(cli, "MODEL_PATH", api.MODEL_PATH)
    monkeypatch.setattr(cli, "Predictor", lambda: api.Predictor(api.MODEL_PATH))
    assert cli.main([str(path)]) == 0
    assert "ALERTE" in capsys.readouterr().out
