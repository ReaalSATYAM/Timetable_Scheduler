import random
import numpy as np
import csv

# Constants
SECTIONS = ['K1', 'K2', 'L1', 'L2']
WORKING_DAYS = 6
TOTAL_SLOTS = 10
MAX_CLASSES_PER_DAY = 7

# Room and lab definitions
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
    1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'
}

# Subjects and weekly counts
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

# Faculty assigned
faculty_map = {
    'TCS402': 'DR. AJAY SHUKLA',
    'TCS403': 'MR. SAURABH AGARWAL',
    'TCS408': 'MR. AKASH CHAUHAN',
    'TCS409': 'MR. SIDDHANT THAPLIYAL',
    'TCS464': 'DR. AMIT GUPTA',
    'XCS401': 'MR. GAURAV',
    'PCS403': 'MS. JYOTI RAMOLA',
    'PCS409': 'DR. VIKRANT SHARMA',
    'PCS464': 'DR. AMIT GUPTA',
    'PESE400': 'MR. DIGAMBAR DHYANI'
}

room_keys = list(rooms.keys())

# Global room and faculty usage tracker
global_used_rooms = [[set() for _ in range(TOTAL_SLOTS)] for _ in range(WORKING_DAYS)]
global_used_faculty = [[set() for _ in range(TOTAL_SLOTS)] for _ in range(WORKING_DAYS)]

# Section-wise timetable generation
for section in SECTIONS:
    print(f"\n📘 Generating timetable for Section {section}...")

    time_table = np.full((WORKING_DAYS, TOTAL_SLOTS), '', dtype=object)
    units_per_day = [0] * WORKING_DAYS
    next_free_slot = [0] * WORKING_DAYS
    used_rooms = [[set() for _ in range(TOTAL_SLOTS)] for _ in range(WORKING_DAYS)]
    daily_subjects = [set() for _ in range(WORKING_DAYS)]

    room_index = 0
    cs_lab_index = 0
    micro_lab_index = 0

    for subject, count in subject_weekly_count.items():
        units_required = 2 if subject.startswith('P') or subject == 'TCS409' else 1
        attempts = 0
        scheduled = 0

        while scheduled < count and attempts < 300:
            day = random.randint(0, WORKING_DAYS - 1)
            slot = next_free_slot[day]

            if subject in daily_subjects[day] or units_per_day[day] + units_required > MAX_CLASSES_PER_DAY or slot + units_required > TOTAL_SLOTS:
                attempts += 1
                continue

            if any(time_table[day][slot + offset] != '' for offset in range(units_required)):
                attempts += 1
                continue

            # Room assignment
            while True:
                if subject in ['PCS409', 'PCS464']:
                    lab = CS_Labs[cs_lab_index % len(CS_Labs)]
                    if all(lab not in used_rooms[day][slot + offset] and lab not in global_used_rooms[day][slot + offset] for offset in range(units_required)):
                        room_assigned = lab
                        cs_lab_index += 1
                        break
                    cs_lab_index += 1
                elif subject == 'PCS403':
                    lab = Micro_Labs[micro_lab_index % len(Micro_Labs)]
                    if all(lab not in used_rooms[day][slot + offset] and lab not in global_used_rooms[day][slot + offset] for offset in range(units_required)):
                        room_assigned = lab
                        micro_lab_index += 1
                        break
                    micro_lab_index += 1
                else:
                    room_id = room_keys[room_index % len(room_keys)]
                    room = rooms[room_id]
                    if all(room not in used_rooms[day][slot + offset] and room not in global_used_rooms[day][slot + offset] for offset in range(units_required)):
                        room_assigned = room
                        room_index += 1
                        break
                    room_index += 1

            faculty = faculty_map[subject]
            if any(faculty in global_used_faculty[day][slot + offset] for offset in range(units_required)):
                attempts += 1
                continue

            # Assign to timetable
            for offset in range(units_required):
                time_table[day][slot + offset] = f"{subject} ({room_assigned}) - {faculty}"
                used_rooms[day][slot + offset].add(room_assigned)
                global_used_rooms[day][slot + offset].add(room_assigned)
                global_used_faculty[day][slot + offset].add(faculty)

            daily_subjects[day].add(subject)
            next_free_slot[day] += units_required
            units_per_day[day] += units_required
            scheduled += 1
            attempts = 0

    # Save section-wise timetable
    with open(f'timetable_s_{section}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['Day/Slot'] + [slots[i + 1] for i in range(TOTAL_SLOTS)]
        writer.writerow(header)
        for i, row in enumerate(time_table):
            writer.writerow([days[i + 1]] + list(row))

print("✅ All section-wise timetables saved.\n")

# Generate vacant room report across all sections
vacant_tracker = [[set(all_rooms) for _ in range(TOTAL_SLOTS)] for _ in range(WORKING_DAYS)]
for section in SECTIONS:
    try:
        with open(f'timetable_s_{section}.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for i, row in enumerate(reader):
                for j in range(1, TOTAL_SLOTS + 1):
                    entry = row[j]
                    if entry.strip():
                        start = entry.find('(')
                        end = entry.find(')')
                        if start != -1 and end != -1:
                            room = entry[start + 1:end]
                            vacant_tracker[i][j - 1].discard(room)
    except FileNotFoundError:
        print(f"❌ Missing file: timetable_s_{section}.csv")

# Save vacant room data
with open('vacant_classes_all_sections.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    header = ['Day/Slot'] + [slots[i + 1] for i in range(TOTAL_SLOTS)]
    writer.writerow(header)
    for i in range(WORKING_DAYS):
        row = [days[i + 1]]
        for j in range(TOTAL_SLOTS):
            row.append(', '.join(sorted(vacant_tracker[i][j])) if vacant_tracker[i][j] else '---')
        writer.writerow(row)

print("✅ Vacant class info saved to 'vacant_classes_all_sections.csv'")

