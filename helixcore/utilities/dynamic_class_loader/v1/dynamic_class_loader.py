import os
import inspect
import importlib.util
from pathlib import Path
from typing import Type, List, Any
import abc


class DynamicClassLoader[T]:
    def __init__(self, base_class: Type[T], folder_path: Path | str):
        self.base_class: Type[T] = base_class
        self.folder_path: Path | str = folder_path

    def find_subclasses(self) -> List[Type[T]]:
        subclasses = []

        # Iterate through files in the specified folder
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                file_path = os.path.join(self.folder_path, filename)

                # Dynamically import the module
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                assert spec
                module = importlib.util.module_from_spec(spec)
                assert module
                assert spec.loader
                spec.loader.exec_module(module)

                # Inspect classes in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Skip if:
                    # 1. Not a subclass of base_class
                    # 2. Is the base class itself
                    # 3. Is a Protocol
                    # 4. Is an Abstract Base Class
                    # 5. Is a runtime checkable Protocol
                    is_skippable = (
                        not issubclass(obj, self.base_class)
                        or obj is self.base_class
                        or _is_protocol(obj)
                        or _is_abstract_base_class(obj)
                    )

                    if not is_skippable:
                        subclasses.append(obj)

        return subclasses


def _is_protocol(cls: Type[Any]) -> bool:
    """
    Check if a class is a Protocol

    Handles different ways Protocols can be defined:
    1. Runtime checkable Protocols
    2. Structural Protocols
    """
    return (
        # Check for runtime_checkable Protocols
        hasattr(cls, "_is_protocol")
        or hasattr(cls, "__protocol__")
        or
        # Check for abc.ABC with @runtime_checkable
        (isinstance(cls, type) and hasattr(cls, "__protocol__"))
    )


def _is_abstract_base_class(cls: Type[Any]) -> bool:
    """
    Check if a class is an Abstract Base Class
    """
    return (
        # Check if it's an ABC
        issubclass(cls, abc.ABC)
        or
        # Check for abstract methods
        any(
            getattr(getattr(cls, method), "__isabstractmethod__", False)
            for method in dir(cls)
        )
    )
