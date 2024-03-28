CREATE TABLE IF NOT EXISTS pokemon_stats (
  id SERIAL PRIMARY KEY,
  pokemon_id INTEGER NOT NULL,
  stat VARCHAR(255) NOT NULL,
  value INTEGER NOT NULL,

  constraint fk_pokemon_stats_pokemon_id
    foreign key (pokemon_id)
    references pokemon(id)
    on delete cascade
);