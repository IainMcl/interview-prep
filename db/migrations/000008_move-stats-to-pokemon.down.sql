alter table pokeomon
    drop column hp,
    drop column attack,
    drop column defense,
    drop column special_attack,
    drop column special_defense,
    drop column speed;

create table if not exists pokemon_stats    
(
    id serial primary key,
    pokemon_id integer not null,
    stat VARCHAR(255) NOT NULL,
    value INTEGER NOT NULL,
    foreign key (pokemon_id) references pokemon(id)
);