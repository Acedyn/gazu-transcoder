import pkgutil
import importlib
from types import ModuleType

from gazu_transcoder.utils.logger import logger
from .units import TranslationUnit, ClientModuleUnit, ModuleUnit


def extract_gazu_modules(gazu_package: ModuleType, excluded_previxes: list[str]):
    """
    Find and parse all the modules found in the gazu package into TranslationUnits
    so they can be transcoded in any language.
    """

    gazu_modules: dict[str, ModuleType] = {}
    for module_info in pkgutil.iter_modules(gazu_package.__path__):
        if module_info.ispkg:
            logger.warning(
                "Skipping package %s: Packages are not supported yet", module_info.name
            )
            continue
        if any(module_info.name.startswith(previx) for previx in excluded_previxes):
            logger.debug(
                "Skipping module %s: Module name part of the excluded prefixes %s",
                module_info.name,
                excluded_previxes,
            )
            continue

        module_name = f"gazu.{module_info.name}"
        gazu_modules[module_name] = importlib.import_module(module_name)

    translation_units: dict[str, TranslationUnit] = {}
    # The client package is more complexe than the others and does not follows the same patterns
    if "client" in gazu_modules:
        translation_units["client"] = ClientModuleUnit.from_module(
            gazu_modules.pop("client")
        )
    else:
        logger.error(
            "The client module was not found, the transcoding will continue but the resulting build will probably not work"
        )

    for name, module in gazu_modules.items():
        translation_units[name] = ModuleUnit.from_module(module)
