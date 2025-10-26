import json
from typing import List, Dict, Any, Optional
from io import open

# Versión del formato JSON
JSON_LATEST = 1

class Entry:
    """Representa una Falla/Diagnóstico en la BK."""
    def __init__(self, name: str):
        self.name = name
        self.description = ""
        self.properties: List[str] = [] # Almacena propiedades como strings

    def is_equal(self, name: str) -> bool:
        return self.name.lower() == name.lower()

    def __str__(self):
        props_str = ', '.join(self.properties)
        return f"[{self.name}]: {self.description}\n  Propiedades: {props_str}"

class BaseConocimientos:
    """
    Clase de la base de conocimientos del sistema experto
    """
    def __init__(self):
        self.entries: List[Entry] = []
        self.description = "Base de conocimientos Big Tools"

    def from_json(self, filename: str):
        """Carga una base de conocimientos a partir de un archivo .json"""
        with open(filename, 'r', encoding='utf8') as f:
            data = f.read()

        obj: Dict[str, Any] = json.loads(data)

        if obj['__v'] != JSON_LATEST:
            raise ValueError("Actualizar JSON a nueva versión")

        self.entries = []  # Limpiar antes de cargar
        self.description = obj['description']

        for json_entry in obj['entries']:
            entry = self.get_or_add_entry(str(json_entry['name']))
            entry.description = str(json_entry['description'])
            # Asumiendo que 'props' es una lista de strings en el JSON
            entry.properties = [str(prop) for prop in json_entry.get('props', [])]

        return self

    def to_json(self, filename: str) -> str:
        """Guarda la base de conocimientos a un archivo .json"""
        obj = {'__v': JSON_LATEST, 'description': self.description, 'entries': []}

        for entry in self.entries:
            json_entry = {'name': entry.name, 'description': entry.description, 'props': entry.properties}
            obj['entries'].append(json_entry)

        data = json.dumps(obj, indent=2)
        with open(filename, 'w', encoding='utf8') as f:
            f.write(data)
        return data

    def get_or_add_entry(self, name: str) -> Entry:
        """Obtiene una entrada de la base de conocimiento, o la agrega si no existe"""
        for entry in self.entries:
            if entry.is_equal(name):
                return entry

        entry = Entry(name)
        self.entries.append(entry)
        return entry
    
    def get_all_props(self) -> List[str]:
        """Devuelve una lista de todas las propiedades únicas en la BK."""
        all_props = set()
        for entry in self.entries:
            all_props.update(entry.properties)
        return list(all_props)
