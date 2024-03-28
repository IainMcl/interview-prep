alter table pokemon_abilities add constraint pokemon_abilities_unique UNIQUE (pokemon_id, ability);

alter table pokemon_types add constraint pokemon_types_unique UNIQUE (pokemon_id, type);