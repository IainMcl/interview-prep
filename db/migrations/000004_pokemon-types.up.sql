CREATE TABLE IF NOT EXISTS pokemon_types (
  id SERIAL PRIMARY KEY,
  pokemon_id INTEGER NOT NULL,
  type VARCHAR(255) NOT NULL,

  constraint fk_pokemon_types_pokemon_id
  foreign key (pokemon_id)
  references pokemon(id)
  on delete cascade
);