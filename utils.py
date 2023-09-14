import os, inspect, importlib
from beanie import Document, View


def all_models() -> list[str]:
    classes = []
    for f in os.listdir('models'):
        if f != '__pycache__':
            try:
                for (name, cls) in inspect.getmembers(importlib.import_module(f"models.{f.split('.')[0]}"), inspect.isclass):
                    x = f'{cls.__module__}.{name}'
                    if (issubclass(cls, Document) or issubclass(cls, View)) and x.startswith('models'):
                    # if x.startswith('models') and 'enums' not in x:
                        classes.append(x) if x not in classes else 0
            except Exception as e:
                print(e)
    return classes