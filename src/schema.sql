-- SQLite Schema
drop table if exists `worlds`;
create table `worlds` (
    `id` integer primary key autoincrement,
    `state` text not null
);
