import json
from pathlib import Path
from typing import Set, Dict

class Territory:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.borders: Set[Territory] = set()
        self.continent: Continent = None

    def __repr__(self):
        return f"Territory(id={self.id}, name={self.name}, borders={", ".join(border.name for border in self.borders)}, continent={self.continent.name})"

class Continent:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.territories: Set[Territory] = set()
        self.bonus: int = None

    def __repr__(self):
        return f"Continent(id={self.id}, name={self.name}, territories={", ".join(territory.name for territory in self.territories)}, bonus={self.bonus})"

class RiskMap:
    def __init__(self, name: str, territories: Dict[int, Territory], continents: Dict[int, Continent]):
        self.name = name
        self.territories = territories
        self.continents = continents
        self.validate()

    @classmethod
    def from_json(cls, path):
        path = Path(path)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        territories: Dict[int, Territory] = {}
        continents: Dict[int, Continent] = {}
        for territory_name in data["territories"]:
            territories[len(territories)] = Territory(len(territories), territory_name)
        for continent_name in data["continents"]:
            continents[len(continents)] = Continent(len(continents), continent_name)
        for territory in territories.values():
            territory.borders = {t for t in territories.values() if t.name in data["borders"][territory.name]}
        for continent in continents.values():
            continent.territories = {t for t in territories.values() if data["territory_to_continent"][t.name] == continent.name}
            continent.bonus = data["continent_bonuses"][continent.name]
            for territory in continent.territories:
                territory.continent = continent

        return cls(data["name"], territories, continents)
    
    def validate(self):
        # Assertion 1: All territories have been assigned to a continent, and the same territory is included in continent.territories
        for territory in self.territories.values():
            assert territory.continent is not None, f"Territory '{territory.name}' is not assigned to a continent"
            assert territory in territory.continent.territories, f"Territory '{territory.name}' is assigned to continent '{territory.continent.name}' but is not in the continent's territories set"
        
        for continent in self.continents.values():
            for territory in continent.territories:
                assert territory.continent == continent, f"Territory '{territory.name}' is in continent '{continent.name}' territories but is assigned to continent '{territory.continent.name}'"
        
        # Assertion 2: The adjacency list is bi-directional (i.e. if A is in B's border list, then B must also be in A's border list)
        for territory in self.territories.values():
            for border in territory.borders:
                assert territory in border.borders, f"Territory '{border.name}' is in '{territory.name}' borders, but '{territory.name}' is not in '{border.name}' borders"
    
    def get_border_ids(self, territory_id: int) -> list[int]:
        return [border.id for border in self.territories[territory_id].borders]
        
    def __repr__(self):
        return f"RiskMap(name={self.name}, territories={len(self.territories)}, continents={len(self.continents)})"

    def __str__(self):
        territories_str = "\n".join(f"{territory_id}: {repr(territory)}" for territory_id, territory in self.territories.items())
        continents_str = "\n".join(f"{continent_id}: {repr(continent)}" for continent_id, continent in self.continents.items())
        return f"{self.name}:\n\nTerritories ({len(self.territories)}):\n{territories_str}\n\nContinents ({len(self.continents)}):\n{continents_str}"
