import requests
from psycopg2 import sql

class PokemonAPI(object):
    def __init__(self, url):
        self.url = url

    def get_pokemon(self, name):
        try:
            response = requests.get(f"{self.url}/pokemon/{name}")
            p = Pokemon.from_json(response.json())
            return p
        except requests.exceptions.RequestException as e:
            print(e)
            return None


class Pokemon(object):
    name = None
    id = None
    height = None
    weight = None
    types = None
    abilities = None
    stats = None
    
    def __init__(self):
        pass

    @staticmethod
    def from_json(json):
        p = Pokemon()
        p.name = json.get("name", "")
        p.id = json.get("id", 0)
        p.height = json.get("height", 0)
        p.weight = json.get("weight", 0)

        types = json.get("types", [])
        p.types = [t['type']['name'] for t in types]

        abilities = json.get("abilities", [])
        p.abilities = [{"name":a['ability']['name'], "hidden": a["is_hidden"]} for a in abilities]

        stats = json.get("stats", [])
        p.stats = {s['stat']['name']: s['base_stat'] for s in stats}
        return p

    def to_json(self):
        return {
            'name': self.name,
            'id': self.id,
            'height': self.height,
            'weight': self.weight,
            'types': self.types,
            'abilities': self.abilities,
            'stats': self.stats
        }
    
    def __str__(self):
        return f"Pokemon: {self.name} (id: {self.id})"
    
    def write_to_database(self, db):
        db.start_transaction()
        db.execute("""
        INSERT INTO pokemon (id, name, height, weight, hp, attack, defense, special_attack, special_defense, speed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (self.id, self.name, self.height, self.weight, self.stats.get("hp", 0), self.stats.get("attack", 0), self.stats.get("defense", 0), self.stats.get("special-attack", 0), self.stats.get("special-defense", 0), self.stats.get("speed", 0))) 

        type_values = [(self.id, t) for t in self.types]
        db.execute_many("""
        INSERT INTO pokemon_types (pokemon_id, type)
        VALUES (%s, %s);
        """, type_values)

        ability_values = [(self.id, a['name'], a['hidden']) for a in self.abilities]
        db.execute_many("""
        INSERT INTO pokemon_abilities (pokemon_id, ability, hidden)
        VALUES (%s, %s, %s);
        """, ability_values)
        db.commit_transaction()

    @staticmethod
    def read_from_database(db, name):
        p = Pokemon()
        p.name = name
        # p.id = db.execute(f"SELECT id FROM pokemon WHERE name = '{name}';")[0][0]
        # p.height = db.execute(f"SELECT height FROM pokemon WHERE name = '{name}';")[0][0]
        # p.weight = db.execute(f"SELECT weight FROM pokemon WHERE name = '{name}';")[0][0]
        # p.types = [t[0] for t in db.execute(f"SELECT type FROM pokemon_types WHERE pokemon_id = {p.id};")]
        # p.abilities = [a[0] for a in db.execute(f"SELECT ability FROM pokemon_abilities WHERE pokemon_id = {p.id};")]
        # p.stats = {s[0]: s[1] for s in db.execute(f"SELECT stat, value FROM pokemon_stats WHERE pokemon_id = {p.id};")}
        return p