import ast
import inspect
from types import ModuleType, FunctionType
from typing import cast, TypedDict
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from gazu_transcoder.utils.logger import logger
from gazu_transcoder.config.types import TranslationTargetConfig
from .grammar import get_function_definition_templated_source


class TranslationUnit(ABC):
    @abstractmethod
    def get_templated_source(self, config: TypedDict) -> str:
        """
        Translate the unit into a string ready to be converted using the jinja template
        engine.
        """


@dataclass
class FunctionUnit(TranslationUnit):
    name: str
    ast: ast.FunctionDef

    @classmethod
    def from_function(cls, function_element: FunctionType):
        """
        Parse the nodes that compose the functions
        """
        # Parsing the function into AST actually returns a new module containing the function alone
        function_ast_module = ast.parse(inspect.getsource(function_element))
        function_ast = cast(ast.FunctionDef, function_ast_module.body[0])

        return cls(function_ast.name, function_ast)

    def get_templated_source(self, config: TranslationTargetConfig):
        return get_function_definition_templated_source(self.ast, config)


@dataclass
class ImportUnit(TranslationUnit):
    name: str
    parents: list[str]

    @classmethod
    def from_module(cls, module: ModuleType):
        import_unit = cls(module.__name__, [])
        return import_unit

    def get_templated_source(self, config: TranslationTargetConfig):
        return ""


@dataclass
class ModuleUnit(TranslationUnit):
    functions: dict[str, FunctionUnit] = field(default_factory=dict)
    imports: dict[str, ImportUnit] = field(default_factory=dict)

    @classmethod
    def from_module(cls, module: ModuleType):
        module_unit = cls()
        module_unit.extract_module_members(module)
        return module_unit

    def extract_module_members(self, module: ModuleType):
        """
        Find and parse the content of a regular module. Every modules that
        does not require a specific treatment is considered as a regular module.
        """

        for name, member in inspect.getmembers(module):
            if isinstance(member, FunctionType):
                logger.debug(
                    "Building translation unit for function %s", member.__name__
                )
                function_unit = FunctionUnit.from_function(member)
                # The function parsing can fail for a lot of reasons
                if not function_unit:
                    logger.error(
                        "Skipping function %s of module %s: Invalid function",
                        name,
                        module.__name__,
                    )
                    continue
                self.functions[name] = function_unit
            elif isinstance(member, ModuleType):
                logger.debug("Building translation unit for module %s", member.__name__)
                self.imports[name] = ImportUnit.from_module(member)

    def get_templated_source(self, config: TranslationTargetConfig):
        return ""


@dataclass
class ClientModuleUnit(ModuleUnit):
    pass
