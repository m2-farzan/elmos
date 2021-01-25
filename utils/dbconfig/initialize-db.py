#!/usr/bin/python3

import json
import mysql.connector
from os import environ


# Connect to the db

db_config = {
    'host': 'db',
    'user': environ['DB_USER'],
    'passwd': environ['DB_PASS'],
    'database': environ['DB_DATABASE']
}
mydb = mysql.connector.connect(**db_config)

print("Connected to database %s as user %s." % (environ['DB_DATABASE'], environ['DB_USER']))


# Get Cursor

mycursor = mydb.cursor()


# Create tables

try:
    mycursor.execute("""
    CREATE TABLE `users` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `password` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `department_id` int(11) DEFAULT NULL,
    `gender` int(11) DEFAULT NULL,
    `last_access` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=789 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    print("Created 'users' table.")
except mysql.connector.errors.ProgrammingError as e:
    if 'already exists' in str(e):
        print("Skipped 'users' table as it already exists.")

try:
    mycursor.execute("""
    CREATE TABLE `units` (
    `id` int(11) NOT NULL,
    `department` int(11) NOT NULL,
    `name` varchar(100) CHARACTER SET utf8mb4 NOT NULL,
    `instructor` varchar(100) CHARACTER SET utf8mb4 DEFAULT NULL,
    `schedule` varchar(100) NOT NULL,
    `exam_day` int(11) DEFAULT NULL,
    `exam_time` decimal(10,2) DEFAULT NULL,
    `capacity` int(11) DEFAULT NULL,
    `registered_count` int(11) DEFAULT NULL,
    `weight` int(11) DEFAULT NULL,
    `gender` int(11) DEFAULT NULL,
    `obsolete` int(2) DEFAULT 0,
    PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    print("Created 'units' table.")
except mysql.connector.errors.ProgrammingError as e:
    if 'already exists' in str(e):
        print("Skipped 'units' table as it already exists.")

try:
    mycursor.execute("""
    CREATE TABLE `supporters` (
    `id` int(11) DEFAULT NULL,
    `t` timestamp NOT NULL DEFAULT current_timestamp()
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    print("Created 'supporters' table.")
except mysql.connector.errors.ProgrammingError as e:
    if 'already exists' in str(e):
        print("Skipped 'supporters' table as it already exists.")

try:
    mycursor.execute("""
    CREATE TABLE `picks_2` (
    `user_id` int(11) NOT NULL,
    `unit_id` int(11) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    print("Created 'picks_2' table.")
except mysql.connector.errors.ProgrammingError as e:
    if 'already exists' in str(e):
        print("Skipped 'picks_2' table as it already exists.")


# Forced tables

mycursor.execute("""
DROP TABLE IF EXISTS `departments`;
""")
mycursor.execute("""
CREATE TABLE `departments` (
  `id` int(11) NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 DEFAULT NULL,
  `has_students` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""")
print("Created or updated 'departments' table.")


mycursor.execute("""
DROP TABLE IF EXISTS `comdeps`;
""")
mycursor.execute("""
CREATE TABLE `comdeps` (
  `id` int(11) NOT NULL,
  `dispname` varchar(100) CHARACTER SET utf8mb4 DEFAULT NULL,
  `sortorder` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""")
print("Created or updated 'comdeps' table.")


# Load json

inputfile_groups = 'groups.json'
inputfile_comgps = 'comgps.json'


with open(inputfile_groups, 'r') as file:
    groups = json.load(file)
with open(inputfile_comgps, 'r') as file:
    comgps = json.load(file)


# Appy data
for id, v in groups.items():
    mycursor.execute("INSERT INTO departments(id, name, has_students) values(%s, %s, %s)",
        (id, v['dispname'], v['has_students']))
print("Inserted 'departments' data.")

for id, v in comgps.items():
    mycursor.execute("INSERT INTO comdeps(id, dispname, sortorder) values(%s, %s, %s)",
        (id, v['dispname'], v['sortorder']))
print("Inserted 'comdeps' data.")


# Commit

mydb.commit()