import os
from shutil import rmtree

from pathlib import Path
from typing import Protocol, runtime_checkable


from helixcore.utilities.dynamic_class_loader.v1.dynamic_class_loader import (
    DynamicClassLoader,
)


# Create a base protocol/class for testing
@runtime_checkable
class Animal(Protocol):
    def make_sound(self) -> str:
        pass


def test_dynamic_class_loader() -> None:
    """Test dynamic class loading functionality."""

    # Create test module files
    dog_content = """
from typing import Protocol, runtime_checkable

@runtime_checkable
class Animal(Protocol):
    def make_sound(self) -> str:
        ...

class Dog:
    def make_sound(self) -> str:
        return "Woof!"
    """

    cat_content = """
from typing import Protocol, runtime_checkable

@runtime_checkable
class Animal(Protocol):
    def make_sound(self) -> str:
        ...

class Cat:
    def make_sound(self) -> str:
        return "Meow!"
    """

    data_dir: Path = Path(__file__).parent.joinpath("./")

    temp_folder = data_dir.joinpath("../temp")
    if os.path.isdir(temp_folder):
        rmtree(temp_folder)
    os.makedirs(temp_folder)

    # Write files
    with open(os.path.join(temp_folder, "dog.py"), "w") as f:
        f.write(dog_content)

    with open(os.path.join(temp_folder, "cat.py"), "w") as f:
        f.write(cat_content)

    # Create a DynamicClassLoader instance
    loader = DynamicClassLoader(base_class=Animal, folder_path=temp_folder)  # type: ignore[type-abstract]

    # Find subclasses
    subclasses = loader.find_subclasses()

    # Verify subclasses
    assert len(subclasses) == 2

    # Verify class names
    class_names = {cls.__name__ for cls in subclasses}
    assert class_names == {"Dog", "Cat"}

    # Verify method functionality
    for cls in subclasses:
        instance = cls()
        assert hasattr(instance, "make_sound")
        assert callable(instance.make_sound)


def test_dynamic_class_loader_empty_dir() -> None:
    """Test behavior with an empty directory."""
    data_dir: Path = Path(__file__).parent.joinpath("./")

    temp_folder = data_dir.joinpath("../temp")
    if os.path.isdir(temp_folder):
        rmtree(temp_folder)
    os.makedirs(temp_folder)

    loader = DynamicClassLoader(base_class=Animal, folder_path=temp_folder)  # type: ignore[type-abstract]
    subclasses = loader.find_subclasses()

    assert len(subclasses) == 0


def test_dynamic_class_loader_init() -> None:
    """Test the initialization of DynamicClassLoader."""
    data_dir: Path = Path(__file__).parent.joinpath("./")

    temp_folder = data_dir.joinpath("../temp")
    if os.path.isdir(temp_folder):
        rmtree(temp_folder)
    os.makedirs(temp_folder)

    loader = DynamicClassLoader(base_class=Animal, folder_path=temp_folder)  # type: ignore[type-abstract]

    assert loader.base_class == Animal
    assert loader.folder_path == Path(temp_folder)
