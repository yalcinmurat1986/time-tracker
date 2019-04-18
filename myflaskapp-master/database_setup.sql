create database timetracker;

use timetracker;

create table company(company_name varchar(100), company_mail_address varchar(500), POC_name varchar(35), POC_email varchar(35), POC_phone_number int(15));

create table employees(employee_id int(11) auto_increment primary key,
first_name varchar(25), last_name varchar(25), email varchar(100), username varchar(30) unique, user_password varchar(100),  register_date timestamp default current_timestamp);


create table jobs(job_id int(11) auto_increment primary key,
job_name varchar(25), company varchar(25), who_created varchar(35), username varchar(30) unique, status enum('completed','active'),  create_date timestamp default current_timestamp);


create table jobtracker(employee_id int(11), 
job_id int(11), work_date date, start_time time, end_time time, worked_time int(11), create_date timestamp default current_timestamp, description varchar(1000));
