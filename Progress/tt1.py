import random
import numpy as np
import csv

# Constants
WORKING_DAYS = 5
TOTAL_SLOTS = 10
MAX_CLASSES_PER_DAY = 7

# Room maps
rooms = {
    1: '101', 2: '102', 3: '103', 4: '104', 5: '105', 6: '106',
    7: '201', 8: '202', 9: '203', 10: '204', 11: '205', 12: '206', 13: '207',
    14: '301', 15: '302', 16: '303',
    17: 'Lt201', 18: 'Lt202', 19: 'Lt301', 20: 'Lt302'
}
CS_Labs = ['Lab1', 'Lab2', 'Lab3', 'Lab4']
Micro_Labs = ['Micro1', 'Micro2', 'Micro3', 'Micro4']
all_rooms = list(rooms.values()) + CS_Labs + Micro_Labs

slots = {
    1: '8:00-8:55', 2: '8:55-9:50', 3: '10:10-11:05', 4: '11:05-12:00', 5: '12:00-12:55',
    6: '12:55-1:50', 7: '2:10-3:05', 8: '3:05-4:00', 9: '4:00-4:55', 10: '4:55-5:50'
}
days = {
    1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday'
}

# Subject-wise weekly slot requirement
subject_weekly_count = {
    'TCS464': 3,
    'TCS402': 3,
    'TCS403': 3,
    'TCS409': 2,
    'TCS408': 3,
    'PCS464': 1,
    'PCS403': 2,
    'PCS409': 2,
    'XCS401': 2,
    'PESE400': 1
}

# Faculty for each subject
faculty_map = {
    'TCS402': ['DR. AJAY SHUKLA'],
    'TCS403': ['MR. SAURABH AGARWAL'],
    'TCS408': ['MR. AKASH CHAUHAN'],
    'TCS409': ['MR. SIDDHANT THAPLIYAL'],
    'TCS464': ['DR. AMIT GUPTA'],
    'XCS401': ['MR. GAURAV', 'MS. GEETIKA'],
    'PCS403': ['MS. JYOTI RAMOLA'],
    'PCS409': ['DR. VIKRANT SHARMA'],
    'PCS464': ['DR. AMIT GUPTA'],
    'PESE400': ['MR. DIGAMBAR DHYANI']
}

# Initialize timetable
time_table = np.full((WORKING_DAYS, TOTAL_SLOTS), '', dtype=object)
units_per_day = [0] * WORKING_DAYS
next_free_slot = [0] * WORKING_DAYS
used_rooms = [[set() for _ in range(TOTAL_SLOTS)] for _ in range(WORKING_DAYS)]

room_keys = list(rooms.keys())
room_index = 0
cs_lab_index = 0
micro_lab_index = 0

# Timetable assignment
for subject, count in subject_weekly_count.items():
    units_required = 2 if subject.startswith('P') or subject == 'TCS409' else 1

    eligible_days = [
        i for i in range(WORKING_DAYS)
        if units_per_day[i] + units_required <= MAX_CLASSES_PER_DAY and
           next_free_slot[i] + units_required <= TOTAL_SLOTS
    ]

    if len(eligible_days) < count:
        print(f"⚠️ Not enough days for {subject} - assigning {len(eligible_days)} of {count}.")

    chosen_days = random.sample(eligible_days, min(count, len(eligible_days)))

    for day in chosen_days:
        slot = next_free_slot[day]
        if any(time_table[day][slot + offset] != '' for offset in range(units_required)):
            print(f"⚠️ Slot collision for {subject} on Day {day + 1} at slot {slot}")
            continue

        # Assign room
        if subject == 'PCS409':
            while True:
                lab = CS_Labs[cs_lab_index % len(CS_Labs)]
                if all(lab not in used_rooms[day][slot + offset] for offset in range(units_required)):
                    break
                cs_lab_index += 1
            room_assigned = lab
            cs_lab_index += 1

        elif subject == 'PCS403':
            while True:
                lab = Micro_Labs[micro_lab_index % len(Micro_Labs)]
                if all(lab not in used_rooms[day][slot + offset] for offset in range(units_required)):
                    break
                micro_lab_index += 1
            room_assigned = lab
            micro_lab_index += 1

        else:
            while True:
                room_id = room_keys[room_index % len(room_keys)]
                room = rooms[room_id]
                if all(room not in used_rooms[day][slot + offset] for offset in range(units_required)):
                    break
                room_index += 1
            room_assigned = room
            room_index += 1

        # Assign faculty
        faculty_list = faculty_map.get(subject, ['TBD'])
        faculty = random.choice(faculty_list)

        for offset in range(units_required):
            time_table[day][slot + offset] = f"{subject} ({room_assigned}) - {faculty}"
            used_rooms[day][slot + offset].add(room_assigned)

        next_free_slot[day] += units_required
        units_per_day[day] += units_required

# Save timetable to CSV
with open('timetable.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    header = ['Day/Slot'] + [slots[i + 1] for i in range(TOTAL_SLOTS)]
    writer.writerow(header)
    for i, row in enumerate(time_table):
        writer.writerow([days[i + 1]] + list(row))

print("✅ Timetable saved to 'timetable.csv'")

# Generate vacant class report
vacant_rooms = [[set(all_rooms) for _ in range(TOTAL_SLOTS)] for _ in range(WORKING_DAYS)]

for day in range(WORKING_DAYS):
    for slot in range(TOTAL_SLOTS):
        entry = time_table[day][slot]
        if entry != '':
            start = entry.find('(')
            end = entry.find(')')
            if start != -1 and end != -1:
                room_used = entry[start + 1:end]
                if room_used in vacant_rooms[day][slot]:
                    vacant_rooms[day][slot].remove(room_used)

with open('vacant_classes.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    header = ['Day/Slot'] + [slots[i + 1] for i in range(TOTAL_SLOTS)]
    writer.writerow(header)
    for i in range(WORKING_DAYS):
        row = [days[i + 1]]
        for j in range(TOTAL_SLOTS):
            row.append(', '.join(sorted(vacant_rooms[i][j])) if vacant_rooms[i][j] else '---')
        writer.writerow(row)

print("✅ Vacant room info saved to 'vacant_classes.csv'")
