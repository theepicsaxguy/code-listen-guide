import logging
from pathlib import Path
from typing import Any, Dict, List

try:
    import tree_sitter_python
    from tree_sitter import Language, Parser

    PYTHON_LANGUAGE = Language(tree_sitter_python.language())
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False

try:
    import tree_sitter_javascript
    import tree_sitter_typescript

    JS_LANGUAGE = Language(tree_sitter_javascript.language())
    TS_LANGUAGE = Language(tree_sitter_typescript.language_typescript())
    HAS_JS_PARSERS = True
except ImportError:
    HAS_JS_PARSERS = False

logger = logging.getLogger(__name__)


def _parse_python_file(file_path: Path) -> Dict[str, Any]:
    """Parse a Python file and extract functions, classes, and imports."""
    if not HAS_TREE_SITTER:
        return {"functions": [], "classes": [], "imports": [], "error": "tree-sitter not available"}

    try:
        with open(file_path, "rb") as f:
            source_code = f.read()

        parser = Parser(PYTHON_LANGUAGE)
        tree = parser.parse(source_code)
        root_node = tree.root_node

        functions = []
        classes = []
        imports = []

        def traverse(node):
            if node.type == "function_definition":
                func_name_node = node.child_by_field_name("name")
                if func_name_node:
                    functions.append(func_name_node.text.decode("utf-8"))
            elif node.type == "class_definition":
                class_name_node = node.child_by_field_name("name")
                if class_name_node:
                    classes.append(class_name_node.text.decode("utf-8"))
            elif node.type in ("import_statement", "import_from_statement"):
                imports.append(node.text.decode("utf-8").strip())

            for child in node.children:
                traverse(child)

        traverse(root_node)

        return {"functions": functions, "classes": classes, "imports": imports}
    except Exception as e:
        logger.warning(f"Failed to parse {file_path}: {e}")
        return {"functions": [], "classes": [], "imports": [], "error": str(e)}


def _parse_javascript_file(file_path: Path) -> Dict[str, Any]:
    """Parse a JavaScript/TypeScript file and extract functions and classes."""
    if not HAS_JS_PARSERS:
        return {"functions": [], "classes": [], "imports": [], "error": "JS parsers not available"}

    try:
        with open(file_path, "rb") as f:
            source_code = f.read()

        is_typescript = file_path.suffix in {".ts", ".tsx"}
        parser = Parser(TS_LANGUAGE if is_typescript else JS_LANGUAGE)
        tree = parser.parse(source_code)
        root_node = tree.root_node

        functions = []
        classes = []
        imports = []

        def traverse(node):
            if node.type in ("function_declaration", "method_definition", "arrow_function"):
                # Try to get function name
                name_node = node.child_by_field_name("name")
                if name_node:
                    functions.append(name_node.text.decode("utf-8"))
            elif node.type == "class_declaration":
                class_name_node = node.child_by_field_name("name")
                if class_name_node:
                    classes.append(class_name_node.text.decode("utf-8"))
            elif node.type in ("import_statement", "import_clause"):
                imports.append(node.text.decode("utf-8").strip())

            for child in node.children:
                traverse(child)

        traverse(root_node)

        return {"functions": functions, "classes": classes, "imports": imports}
    except Exception as e:
        logger.warning(f"Failed to parse {file_path}: {e}")
        return {"functions": [], "classes": [], "imports": [], "error": str(e)}


def build_code_map(path: str) -> Dict[str, Any]:
    """
    Build a comprehensive code map of the repository.

    Parses Python, JavaScript, and TypeScript files to extract:
    - Functions and methods
    - Classes
    - Import statements

    Args:
        path: Path to the cloned repository

    Returns:
        Dictionary with file paths as keys and their parsed contents
    """
    root = Path(path)
    modules: Dict[str, Any] = {}
    file_count = 0
    parsed_count = 0

    # Extensions we can parse
    parseable_extensions = {".py", ".js", ".jsx", ".ts", ".tsx"}

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        # Skip hidden directories and common non-source directories
        if any(part.startswith(".") or part in {"node_modules", "__pycache__", "dist", "build"} for part in file_path.parts):
            continue

        if file_path.suffix in parseable_extensions:
            file_count += 1
            relative_path = str(file_path.relative_to(root))

            if file_path.suffix == ".py":
                result = _parse_python_file(file_path)
            elif file_path.suffix in {".js", ".jsx", ".ts", ".tsx"}:
                result = _parse_javascript_file(file_path)
            else:
                continue

            modules[relative_path] = result
            if "error" not in result:
                parsed_count += 1

    return {
        "modules": modules,
        "summary": {
            "total_files_found": file_count,
            "successfully_parsed": parsed_count,
            "failed_to_parse": file_count - parsed_count,
        },
    }
