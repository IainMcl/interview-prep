CREATE TABLE IF NOT EXISTS pokemon_abilitys (
  id SERIAL PRIMARY KEY,
  pokemon_id INTEGER NOT NULL,
  ability VARCHAR(255) NOT NULL,

constraint fk_pokemon_abilitys_pokemon_id
        foreign key (pokemon_id)
        references pokemon(id)
        on delete cascade
);