#!/usr/bin/python3

import json
import re
import xml.etree.ElementTree as XMLET


# Parse Args

inputfile = 'data_avail.xml'
outputfile_departments = 'departments.json'
outputfile_groups = 'groups.json'
outputfile_comgps = 'comgps.json'


# Load XML

with open(inputfile, 'r') as xmlfile:
    xmldata = xmlfile.read()

xmldata = re.sub('ي', 'ی', xmldata)
xmldata = re.sub('ك', 'ک', xmldata)

root = XMLET.fromstring(xmldata)


# Parse data
departments = {}
groups = {}
comgps = {}

for row in root:
    department_id = row.attrib['B2']
    department_name = row.attrib['B3']
    group_id = row.attrib['B4']
    group_name = row.attrib['B5']
    
    group_fullname = department_name + ' | ' + group_name
    group_has_students = not re.search('عمومی|معارف|ورزش|بدنی|مشترک|زبان', group_fullname)

    group_is_common = re.search('عمومی|معارف|ورزش|بدنی|مشترک|ریاضی|فیزیک|زبان', group_fullname)

    group_level = 1
    if re.search('فوق|ارشد|تکمیلی', group_fullname):
        group_level = 2
    if re.search('دکتری', group_fullname):
        group_level = 3

    departments[department_id] = {
        'name': department_name,
        'has_students': group_has_students,
    }

    groups[department_id + group_id] = {
        'id': department_id + group_id,
        'department_id': department_id,
        'group_id': group_id,
        'name': group_name,
        'dispname': group_fullname,
        'has_students': group_has_students,
        'level': group_level,
    }

    if group_is_common:
        comgps[department_id + group_id] = {
            'id': department_id + group_id,
            'department_id': department_id,
            'group_id': group_id,
            'dispname': group_fullname,
            'sortorder': 1,
        }


# Save json
with open(outputfile_departments, 'w') as file:
    json.dump(departments, file, ensure_ascii=False, indent=4)
with open(outputfile_groups, 'w') as file:
    json.dump(groups, file, ensure_ascii=False, indent=4)
with open(outputfile_comgps, 'w') as file:
    json.dump(comgps, file, ensure_ascii=False, indent=4)