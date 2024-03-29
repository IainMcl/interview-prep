import requests
# from psycopg2 import sql
from requests.models import Response
from database.Database import Database
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class PokemonAPI(object):
    def __init__(self, url):
        self.url: str = url

    def get_pokemon(self, name: str) -> 'Pokemon':
        try:
            response: Response = requests.get(f"{self.url}/pokemon/{name}")
            p: Pokemon = Pokemon.from_json(response.json())
            logger.debug(f"Got pokemon {p}")
            return p
        except requests.exceptions.RequestException as e:
            logger.error(e)
            return None


class Pokemon(object):
    name: str = None
    id: int = None
    height: int = None
    weight: int = None
    types: list[str] = None
    abilities: list[dict[str, str]] = None
    stats: dict[str, int] = None

    def __init__(self, name: str = None, id: int = None, height: int = None, weight: int = None, types: list[str] = None, abilities: list[dict[str, str]] = None, stats: dict[str, int] = None):
        self.name = name
        self.id = id
        self.height = height
        self.weight = weight
        self.types = types
        self.abilities = abilities
        self.stats = stats

    def __str__(self) -> str:
        return f"Pokemon: {self.name} (id: {self.id})"

    def __repr__(self) -> str:
        return f"""
        Pokemon: {self.name} (id: {self.id})
            Height: {self.height}
            Weight: {self.weight}
            Types: {self.types} 
            Abilities: {self.abilities}
            Stats: {self.stats}
        """

    def base_stat_total(self) -> int:
        return sum(self.stats.values())

    @classmethod
    def from_json(cls, json: str) -> 'Pokemon':
        p = Pokemon()
        p.name = json.get("name", "")
        p.id = json.get("id", 0)
        p.height = json.get("height", 0)
        p.weight = json.get("weight", 0)

        types = json.get("types", [])
        p.types = [t['type']['name'] for t in types]

        abilities = json.get("abilities", [])
        p.abilities = [{"name": a['ability']['name'],
                        "hidden": a["is_hidden"]} for a in abilities]

        stats = json.get("stats", [])
        p.stats = {s['stat']['name']: s['base_stat'] for s in stats}
        return p

    def to_json(self) -> str:
        return {
            'name': self.name,
            'id': self.id,
            'height': self.height,
            'weight': self.weight,
            'types': self.types,
            'abilities': self.abilities,
            'stats': self.stats
        }

    def write_to_database(self, db: Database):
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

        ability_values = [(self.id, a['name'], a['hidden'])
                          for a in self.abilities]
        db.execute_many("""
        INSERT INTO pokemon_abilities (pokemon_id, ability, hidden)
        VALUES (%s, %s, %s);
        """, ability_values)
        db.commit_transaction()

    @classmethod
    def _from_db_rows(cls, rows: list[tuple]) -> 'Pokemon':
        # convert rows to pandas df
        df = pd.DataFrame(rows, columns=['id', 'name', 'height', 'weight', 'hp', 'attack',
                          'defense', 'special_attack', 'special_defense', 'speed', 'type', 'ability', 'hidden'])
        # Create a unique index for each type and ability of each Pokemon
        df["type"] = df.groupby("id").apply(
            lambda x: x["type"].unique()).reset_index(drop=True)
        df["abilities"] = df.groupby("id").apply(
            lambda x: x[["ability", "hidden"]].to_dict(orient="records")).reset_index(drop=True)

        # remove unuesed columns ability, hidden then rename abilities to ability
        df.drop(columns=["ability", "hidden"], inplace=True)
        df.rename(columns={"abilities": "ability"}, inplace=True)

        # remove duplicates
        df.drop_duplicates(subset="id", inplace=True)

        # Convert to list of Pokemon
        df = df.to_dict(orient="records")
        return [Pokemon(
            name=row["name"],
            id=row["id"],
            height=row["height"],
            weight=row["weight"],
            types=row["type"],
            abilities=row["ability"],
            stats={
                "hp": row["hp"],
                "attack": row["attack"],
                "defense": row["defense"],
                "special-attack": row["special_attack"],
                "special-defense": row["special_defense"],
                "speed": row["speed"]
            }
        ) for row in df]

    @staticmethod
    def read_from_database(db, name: str = None, id: int = None):
        if not name and not id:
            raise ValueError("Must provide either name or id")
        pkm = None
        if name:
            sql = """
                SELECT 
                    p.id, name, height, weight, hp, attack, defense, special_attack, special_defense, speed, type, ability, hidden
                FROM pokemon p 
                JOIN pokemon_types pt ON p.id = pt.pokemon_id
                JOIN pokemon_abilities pa ON p.id = pa.pokemon_id
                WHERE p.name iLike %s;
                """
            pkm: list[tuple] = db.fetch(sql, (name,))

        elif id:
            sql = """
                SELECT 
                    p.id, name, height, weight, hp, attack, defense, special_attack, special_defense, speed, type, ability, hidden
                FROM pokemon p 
                JOIN pokemon_types pt ON p.id = pt.pokemon_id
                JOIN pokemon_abilities pa ON p.id = pa.pokemon_id
                WHERE p.id = %s;
                """
            pkm: list[tuple] = db.fetch(sql, (id,))
        else:
            raise ValueError("Must provide either name or id")

        if not pkm:
            raise ValueError("Pokemon not found")

        p = Pokemon._from_db_rows(pkm)
        return p

    @staticmethod
    def read_all_from_database(db: Database) -> list['Pokemon']:
        sql = """
            SELECT 
                id, name, height, weight, hp, attack, defense, special_attack, special_defense, speed
            FROM pokemon;
            """
        pkms: list[tuple] = db.fetch(sql, ())
        return [Pokemon._from_db_rows(p) for p in pkms]

    @staticmethod
    def get_pokemon_in_range(db: Database, start: int, end: int) -> list['Pokemon']:
        sql = """
            SELECT 
                p.id, name, height, weight, hp, attack, defense, special_attack, special_defense, speed, type, ability, hidden
            FROM pokemon p 
            JOIN pokemon_types pt ON p.id = pt.pokemon_id
            JOIN pokemon_abilities pa ON p.id = pa.pokemon_id
            WHERE p.id BETWEEN %s AND %s;
            """
        pkm: list[tuple] = db.fetch(sql, (start, end))
        return Pokemon._from_db_rows(pkm)

    @staticmethod
    def get_or_fetch_range(db: Database, start: int, end: int, url: str) -> list['Pokemon']:
        try:
            pkm = Pokemon.get_pokemon_in_range(db, start, end)
            ids = [p.id for p in pkm]
        except ValueError:
            pkm = []
            ids = []
        if not pkm or len(ids) != (end - start + 1):
            logger.debug("Not all ids requested in databse. Fetching from api")
            ids_to_get = [i for i in range(start, end+1) if i not in ids]
            api = PokemonAPI(url)
            for i in ids_to_get:
                p = api.get_pokemon(i)
                p.write_to_database(db)
                pkm.append(p)
        return pkm
