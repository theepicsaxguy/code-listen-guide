"""Comprehensive code analyzer using tree-sitter for deep metadata extraction.

This service provides 10x metadata enrichment including:
- Function definitions, signatures, parameters, return types
- Class hierarchies, inheritance, methods
- Imports, exports, dependencies
- Complexity metrics (cyclomatic, cognitive)
- Call graphs and reference maps
- Documentation extraction
- Code statistics (LOC, comment ratio, etc)
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Import tree-sitter parsers
try:
    from tree_sitter import Language, Parser, Node
    import tree_sitter_python as tspython
    import tree_sitter_javascript as tsjavascript
    import tree_sitter_typescript as tstypescript
    HAS_TREE_SITTER = True

    # Try to import additional languages
    try:
        import tree_sitter_go as tsgo
        HAS_GO = True
    except ImportError:
        HAS_GO = False

    try:
        import tree_sitter_rust as tsrust
        HAS_RUST = True
    except ImportError:
        HAS_RUST = False

    try:
        import tree_sitter_java as tsjava
        HAS_JAVA = True
    except ImportError:
        HAS_JAVA = False

    try:
        import tree_sitter_cpp as tscpp
        HAS_CPP = True
    except ImportError:
        HAS_CPP = False

    try:
        import tree_sitter_c_sharp as tscsharp
        HAS_CSHARP = True
    except ImportError:
        HAS_CSHARP = False

except ImportError:
    HAS_TREE_SITTER = False
    logger.warning("tree-sitter not available. Install with: pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript")


@dataclass
class FunctionMetadata:
    """Metadata for a function/method."""
    name: str
    start_line: int
    end_line: int
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False
    is_generator: bool = False
    complexity: int = 1
    calls: List[str] = field(default_factory=list)
    called_by: List[str] = field(default_factory=list)


@dataclass
class ClassMetadata:
    """Metadata for a class."""
    name: str
    start_line: int
    end_line: int
    base_classes: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    is_abstract: bool = False


@dataclass
class ImportMetadata:
    """Metadata for imports."""
    module: str
    items: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    is_from: bool = False
    line: int = 0


@dataclass
class CodeMetrics:
    """Code quality and complexity metrics."""
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    maintainability_index: float = 0.0
    comment_ratio: float = 0.0


class CodeAnalyzer:
    """Comprehensive code analyzer using tree-sitter."""

    def __init__(self):
        """Initialize code analyzer with tree-sitter parsers."""
        if not HAS_TREE_SITTER:
            raise RuntimeError("tree-sitter is not installed")

        self.parsers = {}
        self._init_parsers()

    def _init_parsers(self):
        """Initialize tree-sitter parsers for supported languages."""
        # Python
        python_parser = Parser()
        python_parser.set_language(Language(tspython.language()))
        self.parsers['python'] = python_parser

        # JavaScript
        js_parser = Parser()
        js_parser.set_language(Language(tsjavascript.language()))
        self.parsers['javascript'] = js_parser

        # TypeScript
        ts_parser = Parser()
        ts_lang = tstypescript.language_typescript()
        ts_parser.set_language(Language(ts_lang))
        self.parsers['typescript'] = ts_parser

        # TSX
        tsx_parser = Parser()
        tsx_lang = tstypescript.language_tsx()
        tsx_parser.set_language(Language(tsx_lang))
        self.parsers['tsx'] = tsx_parser

        # Go
        if HAS_GO:
            go_parser = Parser()
            go_parser.set_language(Language(tsgo.language()))
            self.parsers['go'] = go_parser

        # Rust
        if HAS_RUST:
            rust_parser = Parser()
            rust_parser.set_language(Language(tsrust.language()))
            self.parsers['rust'] = rust_parser

        # Java
        if HAS_JAVA:
            java_parser = Parser()
            java_parser.set_language(Language(tsjava.language()))
            self.parsers['java'] = java_parser

        # C++
        if HAS_CPP:
            cpp_parser = Parser()
            cpp_parser.set_language(Language(tscpp.language()))
            self.parsers['cpp'] = cpp_parser

        # C#
        if HAS_CSHARP:
            csharp_parser = Parser()
            csharp_parser.set_language(Language(tscsharp.language()))
            self.parsers['csharp'] = csharp_parser

    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        suffix = file_path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.mjs': 'javascript',
            '.cjs': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'tsx',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.hpp': 'cpp',
            '.h': 'cpp',
            '.cs': 'csharp',
        }
        return language_map.get(suffix)

    def analyze_file(self, file_path: Path, content: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a code file.

        Returns rich metadata including:
        - Functions with signatures, complexity, call graphs
        - Classes with hierarchies and relationships
        - Imports and dependencies
        - Code metrics and statistics
        - Documentation
        """
        if content is None:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

        language = self.detect_language(file_path)
        if not language or language not in self.parsers:
            return self._fallback_analysis(file_path, content, language)

        try:
            parser = self.parsers[language]
            tree = parser.parse(bytes(content, 'utf8'))
            root_node = tree.root_node

            # Extract all metadata
            functions = self._extract_functions(root_node, content, language)
            classes = self._extract_classes(root_node, content, language)
            imports = self._extract_imports(root_node, content, language)
            exports = self._extract_exports(root_node, content, language)

            # Build call graph
            call_graph = self._build_call_graph(functions)

            # Calculate metrics
            metrics = self._calculate_metrics(content, root_node, functions, classes)

            # Extract documentation
            documentation = self._extract_documentation(root_node, content, language)

            # Build dependency map
            dependencies = self._build_dependency_map(imports, exports)

            return {
                'language': language,
                'functions': [self._function_to_dict(f) for f in functions],
                'classes': [self._class_to_dict(c) for c in classes],
                'imports': [self._import_to_dict(i) for i in imports],
                'exports': exports,
                'call_graph': call_graph,
                'metrics': self._metrics_to_dict(metrics),
                'documentation': documentation,
                'dependencies': dependencies,
                'metadata': {
                    'total_functions': len(functions),
                    'total_classes': len(classes),
                    'total_imports': len(imports),
                    'total_exports': len(exports),
                    'has_tests': self._detect_tests(file_path, content),
                    'entry_point': self._detect_entry_point(content, language),
                    'framework': self._detect_framework(imports, content),
                    'patterns': self._detect_patterns(content, classes, functions),
                }
            }

        except Exception as e:
            logger.error(f"Failed to analyze {file_path} with tree-sitter: {e}")
            return self._fallback_analysis(file_path, content, language)

    def _extract_functions(self, root_node: Node, content: str, language: str) -> List[FunctionMetadata]:
        """Extract all function definitions with detailed metadata."""
        functions = []

        # Language-specific node types
        function_types = {
            'python': ['function_definition', 'async_function_definition'],
            'javascript': ['function_declaration', 'function', 'arrow_function', 'method_definition'],
            'typescript': ['function_declaration', 'function', 'arrow_function', 'method_definition', 'method_signature'],
            'tsx': ['function_declaration', 'function', 'arrow_function', 'method_definition'],
            'go': ['function_declaration', 'method_declaration'],
            'rust': ['function_item'],
            'java': ['method_declaration', 'constructor_declaration'],
            'cpp': ['function_definition'],
            'csharp': ['method_declaration', 'constructor_declaration'],
        }

        target_types = function_types.get(language, ['function_definition'])

        def traverse(node: Node):
            if node.type in target_types:
                func = self._parse_function(node, content, language)
                if func:
                    functions.append(func)

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return functions

    def _parse_function(self, node: Node, content: str, language: str) -> Optional[FunctionMetadata]:
        """Parse a function node into FunctionMetadata."""
        try:
            # Get function name
            name_node = None
            for child in node.children:
                if child.type in ['identifier', 'property_identifier', 'field_identifier']:
                    name_node = child
                    break

            if not name_node:
                return None

            name = content[name_node.start_byte:name_node.end_byte]

            # Get parameters
            parameters = []
            params_node = node.child_by_field_name('parameters')
            if params_node:
                parameters = self._parse_parameters(params_node, content, language)

            # Get return type
            return_type = None
            return_node = node.child_by_field_name('return_type')
            if return_node:
                return_type = content[return_node.start_byte:return_node.end_byte]

            # Get docstring
            docstring = self._extract_docstring(node, content, language)

            # Check if async
            is_async = node.type.startswith('async_') or 'async' in content[node.start_byte:node.start_byte+50].lower()

            # Calculate complexity
            complexity = self._calculate_function_complexity(node, content)

            # Extract function calls
            calls = self._extract_function_calls(node, content, language)

            return FunctionMetadata(
                name=name,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                parameters=parameters,
                return_type=return_type,
                docstring=docstring,
                is_async=is_async,
                complexity=complexity,
                calls=calls,
            )

        except Exception as e:
            logger.debug(f"Failed to parse function: {e}")
            return None

    def _parse_parameters(self, params_node: Node, content: str, language: str) -> List[Dict[str, Any]]:
        """Parse function parameters."""
        parameters = []

        for child in params_node.children:
            if child.type in ['identifier', 'parameter', 'required_parameter', 'optional_parameter', 'formal_parameter']:
                param_text = content[child.start_byte:child.end_byte]

                # Try to extract name and type
                param_info = {'name': param_text, 'type': None, 'default': None}

                # Look for type annotation
                type_node = child.child_by_field_name('type')
                if type_node:
                    param_info['type'] = content[type_node.start_byte:type_node.end_byte]

                # Look for default value
                value_node = child.child_by_field_name('value')
                if value_node:
                    param_info['default'] = content[value_node.start_byte:value_node.end_byte]

                parameters.append(param_info)

        return parameters

    def _extract_classes(self, root_node: Node, content: str, language: str) -> List[ClassMetadata]:
        """Extract all class definitions."""
        classes = []

        class_types = {
            'python': ['class_definition'],
            'javascript': ['class_declaration'],
            'typescript': ['class_declaration'],
            'tsx': ['class_declaration'],
            'go': ['type_declaration'],
            'rust': ['struct_item', 'trait_item'],
            'java': ['class_declaration', 'interface_declaration'],
            'cpp': ['class_specifier'],
            'csharp': ['class_declaration', 'interface_declaration'],
        }

        target_types = class_types.get(language, ['class_definition'])

        def traverse(node: Node):
            if node.type in target_types:
                cls = self._parse_class(node, content, language)
                if cls:
                    classes.append(cls)

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return classes

    def _parse_class(self, node: Node, content: str, language: str) -> Optional[ClassMetadata]:
        """Parse a class node into ClassMetadata."""
        try:
            # Get class name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None

            name = content[name_node.start_byte:name_node.end_byte]

            # Get base classes
            base_classes = []
            superclass_node = node.child_by_field_name('superclass') or node.child_by_field_name('interfaces')
            if superclass_node:
                base_text = content[superclass_node.start_byte:superclass_node.end_byte]
                base_classes = [b.strip() for b in base_text.split(',')]

            # Get methods
            methods = []
            body_node = node.child_by_field_name('body')
            if body_node:
                for child in body_node.children:
                    if child.type in ['function_definition', 'method_definition', 'method_declaration']:
                        method_name_node = child.child_by_field_name('name')
                        if method_name_node:
                            methods.append(content[method_name_node.start_byte:method_name_node.end_byte])

            # Get docstring
            docstring = self._extract_docstring(node, content, language)

            return ClassMetadata(
                name=name,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                base_classes=base_classes,
                methods=methods,
                docstring=docstring,
            )

        except Exception as e:
            logger.debug(f"Failed to parse class: {e}")
            return None

    def _extract_imports(self, root_node: Node, content: str, language: str) -> List[ImportMetadata]:
        """Extract import statements."""
        imports = []

        import_types = {
            'python': ['import_statement', 'import_from_statement'],
            'javascript': ['import_statement'],
            'typescript': ['import_statement'],
            'tsx': ['import_statement'],
            'go': ['import_declaration'],
            'rust': ['use_declaration'],
            'java': ['import_declaration'],
            'cpp': ['preproc_include'],
            'csharp': ['using_directive'],
        }

        target_types = import_types.get(language, ['import_statement'])

        def traverse(node: Node):
            if node.type in target_types:
                imp = self._parse_import(node, content, language)
                if imp:
                    imports.append(imp)

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return imports

    def _parse_import(self, node: Node, content: str, language: str) -> Optional[ImportMetadata]:
        """Parse an import node."""
        try:
            import_text = content[node.start_byte:node.end_byte]

            # Extract module and items based on language
            if language == 'python':
                if node.type == 'import_from_statement':
                    # from X import Y
                    parts = import_text.split('import')
                    module = parts[0].replace('from', '').strip()
                    items = [i.strip() for i in parts[1].split(',')]
                    return ImportMetadata(module=module, items=items, is_from=True, line=node.start_point[0] + 1)
                else:
                    # import X
                    module = import_text.replace('import', '').strip()
                    return ImportMetadata(module=module, line=node.start_point[0] + 1)

            elif language in ['javascript', 'typescript', 'tsx']:
                # import X from 'Y'
                if 'from' in import_text:
                    parts = import_text.split('from')
                    module = parts[1].strip().strip('"\'').strip(';')
                    items_part = parts[0].replace('import', '').strip()
                    items = [items_part] if items_part else []
                    return ImportMetadata(module=module, items=items, line=node.start_point[0] + 1)

            return ImportMetadata(module=import_text, line=node.start_point[0] + 1)

        except Exception as e:
            logger.debug(f"Failed to parse import: {e}")
            return None

    def _extract_exports(self, root_node: Node, content: str, language: str) -> List[str]:
        """Extract export statements."""
        exports = []

        export_types = {
            'javascript': ['export_statement'],
            'typescript': ['export_statement'],
            'tsx': ['export_statement'],
        }

        target_types = export_types.get(language, [])
        if not target_types:
            return exports

        def traverse(node: Node):
            if node.type in target_types:
                export_text = content[node.start_byte:node.end_byte]
                exports.append(export_text)

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return exports

    def _extract_function_calls(self, node: Node, content: str, language: str) -> List[str]:
        """Extract function calls within a function."""
        calls = []

        call_types = {
            'python': ['call'],
            'javascript': ['call_expression'],
            'typescript': ['call_expression'],
            'tsx': ['call_expression'],
            'go': ['call_expression'],
            'rust': ['call_expression'],
            'java': ['method_invocation'],
            'cpp': ['call_expression'],
            'csharp': ['invocation_expression'],
        }

        target_types = call_types.get(language, ['call'])

        def traverse(n: Node):
            if n.type in target_types:
                func_node = n.child_by_field_name('function')
                if func_node:
                    call_name = content[func_node.start_byte:func_node.end_byte]
                    calls.append(call_name)

            for child in n.children:
                traverse(child)

        traverse(node)
        return list(set(calls))  # Remove duplicates

    def _extract_docstring(self, node: Node, content: str, language: str) -> Optional[str]:
        """Extract docstring/comment for a function or class."""
        # Look for docstring in first child (Python) or preceding comment
        for child in node.children:
            if child.type in ['string', 'expression_statement', 'comment', 'documentation_comment']:
                text = content[child.start_byte:child.end_byte]
                if text.startswith('"""') or text.startswith("'''") or text.startswith('/*'):
                    return text.strip().strip('"""').strip("'''").strip('/*').strip('*/').strip()

        return None

    def _calculate_function_complexity(self, node: Node, content: str) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        # Count decision points
        decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'switch', 'case', 'catch', 'except', '&&', '||', '?']

        def traverse(n: Node):
            nonlocal complexity
            if n.type in ['if_statement', 'for_statement', 'while_statement', 'switch_statement', 'try_statement']:
                complexity += 1

            for child in n.children:
                traverse(child)

        traverse(node)
        return complexity

    def _calculate_metrics(self, content: str, root_node: Node, functions: List[FunctionMetadata], classes: List[ClassMetadata]) -> CodeMetrics:
        """Calculate comprehensive code metrics."""
        lines = content.split('\n')

        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith('#') or line.strip().startswith('//'))
        code_lines = total_lines - blank_lines - comment_lines

        cyclomatic_complexity = sum(f.complexity for f in functions)

        comment_ratio = comment_lines / total_lines if total_lines > 0 else 0.0

        # Simple maintainability index calculation
        avg_complexity = cyclomatic_complexity / len(functions) if functions else 1
        maintainability_index = max(0, 171 - 5.2 * avg_complexity - 0.23 * cyclomatic_complexity)

        return CodeMetrics(
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            cyclomatic_complexity=cyclomatic_complexity,
            cognitive_complexity=cyclomatic_complexity,  # Simplified
            maintainability_index=maintainability_index,
            comment_ratio=comment_ratio,
        )

    def _build_call_graph(self, functions: List[FunctionMetadata]) -> Dict[str, List[str]]:
        """Build call graph showing function relationships."""
        call_graph = {}

        # Create function name to function mapping
        func_map = {f.name: f for f in functions}

        # Build caller -> callee relationships
        for func in functions:
            call_graph[func.name] = func.calls

            # Update called_by for each callee
            for called_func_name in func.calls:
                if called_func_name in func_map:
                    func_map[called_func_name].called_by.append(func.name)

        return call_graph

    def _extract_documentation(self, root_node: Node, content: str, language: str) -> Dict[str, Any]:
        """Extract all documentation and comments."""
        documentation = {
            'file_docstring': None,
            'comments': [],
            'todos': [],
            'fixmes': [],
        }

        # Extract file-level docstring (first string literal)
        for child in root_node.children:
            if child.type in ['string', 'expression_statement', 'comment']:
                text = content[child.start_byte:child.end_byte]
                if text.startswith('"""') or text.startswith("'''"):
                    documentation['file_docstring'] = text.strip().strip('"""').strip("'''")
                    break

        # Extract all comments
        def traverse(node: Node):
            if node.type == 'comment':
                comment_text = content[node.start_byte:node.end_byte]
                documentation['comments'].append({
                    'text': comment_text,
                    'line': node.start_point[0] + 1,
                })

                # Check for TODOs and FIXMEs
                if 'TODO' in comment_text:
                    documentation['todos'].append({
                        'text': comment_text,
                        'line': node.start_point[0] + 1,
                    })
                if 'FIXME' in comment_text:
                    documentation['fixmes'].append({
                        'text': comment_text,
                        'line': node.start_point[0] + 1,
                    })

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return documentation

    def _build_dependency_map(self, imports: List[ImportMetadata], exports: List[str]) -> Dict[str, Any]:
        """Build dependency map."""
        return {
            'external_dependencies': [imp.module for imp in imports if not imp.module.startswith('.')],
            'internal_dependencies': [imp.module for imp in imports if imp.module.startswith('.')],
            'exported_symbols': len(exports),
        }

    def _detect_tests(self, file_path: Path, content: str) -> bool:
        """Detect if file contains tests."""
        test_indicators = [
            'test_', 'Test', 'describe(', 'it(', '@pytest', '@Test', 'unittest',
            'jest', 'mocha', 'chai'
        ]
        return any(indicator in content for indicator in test_indicators)

    def _detect_entry_point(self, content: str, language: str) -> bool:
        """Detect if file is an entry point."""
        if language == 'python':
            return 'if __name__ == "__main__"' in content
        elif language in ['javascript', 'typescript']:
            return 'process.argv' in content or 'main()' in content
        return False

    def _detect_framework(self, imports: List[ImportMetadata], content: str) -> Optional[str]:
        """Detect framework being used."""
        frameworks = {
            'flask': 'Flask',
            'django': 'Django',
            'fastapi': 'FastAPI',
            'express': 'Express.js',
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'spring': 'Spring',
            'dotnet': '.NET',
        }

        for imp in imports:
            for key, name in frameworks.items():
                if key in imp.module.lower():
                    return name

        # Check content for framework indicators
        for key, name in frameworks.items():
            if key in content.lower():
                return name

        return None

    def _detect_patterns(self, content: str, classes: List[ClassMetadata], functions: List[FunctionMetadata]) -> List[str]:
        """Detect design patterns and architectural patterns."""
        patterns = []

        # Singleton
        if 'Singleton' in content or '_instance' in content:
            patterns.append('Singleton')

        # Factory
        if 'Factory' in content or any('create_' in f.name for f in functions):
            patterns.append('Factory')

        # Observer
        if 'Observer' in content or 'subscribe' in content or 'addEventListener' in content:
            patterns.append('Observer')

        # Decorator
        if any('@' in content[:1000] for _ in range(3)):  # Multiple decorators
            patterns.append('Decorator')

        # Strategy
        if 'Strategy' in content:
            patterns.append('Strategy')

        # MVC/MVVM
        if any(c.name.endswith('Controller') for c in classes):
            patterns.append('MVC')
        if any(c.name.endswith('ViewModel') for c in classes):
            patterns.append('MVVM')

        return patterns

    def _fallback_analysis(self, file_path: Path, content: str, language: Optional[str]) -> Dict[str, Any]:
        """Fallback analysis when tree-sitter fails."""
        lines = content.split('\n')

        return {
            'language': language or 'unknown',
            'functions': [],
            'classes': [],
            'imports': [],
            'exports': [],
            'call_graph': {},
            'metrics': {
                'total_lines': len(lines),
                'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
                'comment_lines': len([l for l in lines if l.strip().startswith('#')]),
                'blank_lines': len([l for l in lines if not l.strip()]),
            },
            'documentation': {'file_docstring': None, 'comments': []},
            'dependencies': {},
            'metadata': {},
        }

    # Helper methods to convert dataclasses to dicts
    def _function_to_dict(self, func: FunctionMetadata) -> Dict[str, Any]:
        return {
            'name': func.name,
            'start_line': func.start_line,
            'end_line': func.end_line,
            'parameters': func.parameters,
            'return_type': func.return_type,
            'docstring': func.docstring,
            'decorators': func.decorators,
            'is_async': func.is_async,
            'is_generator': func.is_generator,
            'complexity': func.complexity,
            'calls': func.calls,
            'called_by': func.called_by,
        }

    def _class_to_dict(self, cls: ClassMetadata) -> Dict[str, Any]:
        return {
            'name': cls.name,
            'start_line': cls.start_line,
            'end_line': cls.end_line,
            'base_classes': cls.base_classes,
            'methods': cls.methods,
            'properties': cls.properties,
            'docstring': cls.docstring,
            'decorators': cls.decorators,
            'is_abstract': cls.is_abstract,
        }

    def _import_to_dict(self, imp: ImportMetadata) -> Dict[str, Any]:
        return {
            'module': imp.module,
            'items': imp.items,
            'alias': imp.alias,
            'is_from': imp.is_from,
            'line': imp.line,
        }

    def _metrics_to_dict(self, metrics: CodeMetrics) -> Dict[str, Any]:
        return {
            'total_lines': metrics.total_lines,
            'code_lines': metrics.code_lines,
            'comment_lines': metrics.comment_lines,
            'blank_lines': metrics.blank_lines,
            'cyclomatic_complexity': metrics.cyclomatic_complexity,
            'cognitive_complexity': metrics.cognitive_complexity,
            'maintainability_index': round(metrics.maintainability_index, 2),
            'comment_ratio': round(metrics.comment_ratio, 2),
        }
