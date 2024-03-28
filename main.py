from database.Database import Database
from pokemon.Pokemon import PokemonAPI
from config import Config

def main():
    c = Config()
    d = Database(
        c.get('database', 'postgres_user'),
        c.get('database', 'postgres_password'),
        c.get('database', 'host'),
        c.get('database', 'port'),
        c.get('database', 'postgres_db')
    )

    d.connect()


    papi = PokemonAPI(c.get('pokemonapi', 'url'))
    for i in range(1, 100):
        pokemon = papi.get_pokemon(i)
        pokemon.write_to_database(d)

    d.disconnect()


if __name__ == "__main__":
    main()