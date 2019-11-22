create table WashU_Pitching;

use WashU_Pitching;
create table Roster (
	first_name varchar(30) not null
);

ALTER TABLE Roster ADD lastname varchar(30) not null;
ALTER TABLE Roster CHANGE first_name firstname varchar(30) not null;
ALTER TABLE Roster ADD class varchar(10) not null;
ALTER TABLE Roster ADD throws varchar(10) not null;
ALTER TABLE Roster ADD number smallint;
ALTER TABLE Roster ADD id mediumint not null auto_increment primary key; 

CREATE TABLE Login_Info (
	firstname varchar(30),
    lastname varchar(30),
	username varchar(30) not null primary key,
    password varchar(30) not null
);