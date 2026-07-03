import importlib.machinery
import importlib.util
from pathlib import Path


def load_bootstrap_module():
    root = Path(__file__).resolve().parents[1]
    script_path = root / "ai-docs-bootstrap"
    loader = importlib.machinery.SourceFileLoader("ai_docs_bootstrap", str(script_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise RuntimeError(f"Unable to build module spec for {script_path}")

    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module
