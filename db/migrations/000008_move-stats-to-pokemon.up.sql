drop table pokemon_stats;

alter table pokemon
    add column hp integer not null default 0,
    add column attack integer not null default 0,
    add column defense integer not null default 0,
    add column special_attack integer not null default 0,
    add column special_defense integer not null default 0,
    add column speed integer not null default 0;
