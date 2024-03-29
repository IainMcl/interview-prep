from database.Database import Database
from pokemon.Pokemon import PokemonAPI, Pokemon
from config import Config, get_database_config
from argparse import ArgumentParser
import logging

logger = logging.getLogger(__name__)


def main():
    c = Config()
    logging.basicConfig(level=c.get('logging', 'level'))
    logger.info("Starting")

    # Parse args
    parser = ArgumentParser()
    parser.add_argument("-n", "--name", help="Pokemon name", type=str)
    parser.add_argument("-i", "--id", help="Pokemon id", type=int)
    parser.add_argument(
        "-g", "--get", help="Get pokemon in id range", type=int, nargs=2)
    args = parser.parse_args()

    db_args = get_database_config(c)

    if args.name:
        with Database(**db_args) as d:
            try:
                p = Pokemon.read_from_database(d, name=args.name)
                logger.info(p)
            except ValueError:
                logger.error(f"Pokemon {args.name} not found")

    elif args.id:
        with Database(**db_args) as d:
            try:
                p = Pokemon.read_from_database(d, id=args.id)
                logger.info(p)
            except ValueError:
                logger.error(f"Pokemon with id {args.id} not found")

    elif args.get:
        with Database(**db_args) as d:
            # Check if they are in the db and if not then get from the api
            max_id = int(c.get('pokemonapi', 'max_id'))
            if args.get[0] < 1 or args.get[1] > max_id:
                logger.error(
                    f"Pokemon id range must be between 1 and {max_id} inclusive")
                return
            try:
                p = Pokemon.get_or_fetch_range(
                    d, args.get[0], args.get[1], c.get('pokemonapi', 'url'))
                for pokemon in p:
                    logger.info(pokemon)
            except ValueError:
                logger.error(
                    f"Pokemon with id {args.get[0]} to {args.get[1]} not found")

    else:
        parser.print_help()
    logger.info("Ending program")


if __name__ == "__main__":
    main()
