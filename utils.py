import os, inspect, importlib


def all_models() -> list[str]:
    classes = []
    for f in os.listdir('models'):
        if f != '__pycache__':
            try:
                for (name, cls) in inspect.getmembers(importlib.import_module(f"models.{f.split('.')[0]}"), inspect.isclass):
                    x = f'{cls.__module__}.{name}'
                    if x.startswith('models') and 'enums' not in x:
                        classes.append(x) if x not in classes else 0
            except Exception as e:
                print(e)
    return classes