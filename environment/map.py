import json
from pathlib import Path
from typing import Set

class Territory:
    def __init__(self, name: str):
        self.name = name
        self.borders: Set[Territory] = set()
        self.continent: Continent = None

    def __repr__(self):
        return f"Territory(name={self.name}, borders={", ".join(border.name for border in self.borders)}, continent={self.continent.name})"

class Continent:
    def __init__(self, name: str):
        self.name = name
        self.territories: Set[Territory] = set()
        self.bonus: int = None

    def __repr__(self):
        return f"Continent(name={self.name}, territories={", ".join(territory.name for territory in self.territories)}, bonus={self.bonus})"

class RiskMap:
    def __init__(self, name, territories: Set[Territory], continents: Set[Continent]):
        self.name = name
        self.territories = territories
        self.continents = continents
        self.validate()

    @classmethod
    def from_json(cls, path):
        path = Path(path)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        territories: Set[Territory] = set()
        continents: Set[Continent] = set()
        for territory_name in data["territories"]:
            territories.add(Territory(territory_name))
        for continent_name in data["continents"]:
            continents.add(Continent(continent_name))
        for territory in territories:
            territory.borders = {t for t in territories if t.name in data["borders"][territory.name]}
        for continent in continents:
            continent.territories = {t for t in territories if data["territory_to_continent"][t.name] == continent.name}
            continent.bonus = data["continent_bonuses"][continent.name]
            for territory in continent.territories:
                territory.continent = continent

        return cls(data["name"], territories, continents)
    
    def validate(self):
        # Assertion 1: All territories have been assigned to a continent, and the same territory is included in continent.territories
        for territory in self.territories:
            assert territory.continent is not None, f"Territory '{territory.name}' is not assigned to a continent"
            assert territory in territory.continent.territories, f"Territory '{territory.name}' is assigned to continent '{territory.continent.name}' but is not in the continent's territories set"
        
        for continent in self.continents:
            for territory in continent.territories:
                assert territory.continent == continent, f"Territory '{territory.name}' is in continent '{continent.name}' territories but is assigned to continent '{territory.continent.name}'"
        
        # Assertion 2: The adjacency list is bi-directional (i.e. if A is in B's border list, then B must also be in A's border list)
        for territory in self.territories:
            for border in territory.borders:
                assert territory in border.borders, f"Territory '{border.name}' is in '{territory.name}' borders, but '{territory.name}' is not in '{border.name}' borders"
        
    def __repr__(self):
        return f"RiskMap(name={self.name}, territories={len(self.territories)}, continents={len(self.continents)})"

    def __str__(self):
        territories_str = "\n".join(repr(territory) for territory in self.territories)
        continents_str = "\n".join(repr(continent) for continent in self.continents)
        return f"{self.name}:\n\nTerritories ({len(self.territories)}):\n{territories_str}\n\nContinents ({len(self.continents)}):\n{continents_str}"
