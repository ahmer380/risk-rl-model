import random

import matplotlib.pyplot as plt
import networkx as nx

class KCliqueGenerator:
    """Generates a k-clique graph with a specified density of edges."""
    @classmethod
    def generate(cls, k: int, density: float, visualise: bool = False):
        assert 0 <= density <= 1, "Density must be between 0 and 1"
        assert density >= 2 / k, "Density must be greater than 2/k to ensure a connected graph"

        map_json = {}
        map_json["name"] = f"{k}_clique_density_{str(density).replace('.', '_')}"
        map_json["territories"] = [f"T_{i}" for i in range(1, k + 1)]
        map_json["continents"] = ["C_Global"]
        map_json["territory_to_continent"] = {f"T_{i}": "C_Global" for i in range(1, k + 1)}
        map_json["continent_bonuses"] = {"C_Global": 0}

        num_borders = int((k * (k - 1) / 2) * density)
        map_borders = {(f"T_{i}", f"T_{i + 1}") for i in range(1, k)} # Start with the minimal chain to ensure connectivity
        all_possible_borders = [(f"T_{i}", f"T_{j}") for i in range(1, k + 1) for j in range(i + 1, k + 1)]
        random.shuffle(all_possible_borders)
        for border in all_possible_borders:
            if len(map_borders) >= num_borders:
                break
            if border not in map_borders and (border[1], border[0]) not in map_borders:
                map_borders.add(border)
        
        map_json["borders"] = {f"T_{i}": [] for i in range(1, k + 1)}
        for border in map_borders:
            map_json["borders"][border[0]].append(border[1])
            map_json["borders"][border[1]].append(border[0])
        
        if visualise:
            KCliqueGenerator.visualise(map_json)
        
        return map_json
    
    @classmethod
    def visualise(cls, map_json):
        G = nx.Graph()
        for territory, neighbors in map_json["borders"].items():
            for neighbor in neighbors:
                G.add_edge(territory, neighbor)
        
        plt.figure(figsize=(8, 8))
        nx.draw_circular(G, with_labels=True, node_size=1000)
        plt.title(map_json["name"])
        plt.show()
