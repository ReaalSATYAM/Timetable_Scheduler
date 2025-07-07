# Updated timetable generator with fixed room-sharing logic and correct slot mapping

import random
import numpy as np
import csv
import pandas as pd

EXCEL_PATH = 'demo.xlsx'
sheets = pd.read_excel(EXCEL_PATH, sheet_name=None)

# === Load Configurations ===
SECTIONS = sheets['Sections']['Section'].dropna().astype(str).tolist()
slots_df = sheets['Slots'].dropna(subset=['Slot_ID'])

slots = dict(zip(slots_df['Slot_ID'].astype(int), slots_df['Time_Range'].astype(str)))
TOTAL_SLOTS = len(slots)

days_df = sheets['Days'].dropna(subset=['Day_ID'])
days = dict(zip(days_df['Day_ID'].astype(int), days_df['Day_Name'].astype(str)))
WORKING_DAYS = len(days)

rooms_df = sheets['Rooms'].dropna(subset=['Room_ID'])
rooms = dict(zip(rooms_df['Room_ID'].astype(int), rooms_df['Room_Name'].astype(str)))
room_keys = list(rooms.keys())

CS_Labs = sheets['CS_Labs']['CS_Lab'].dropna().astype(str).tolist()
Micro_Labs = sheets['Micro_Labs']['Micro_Lab'].dropna().astype(str).tolist()
all_rooms = list(rooms.values()) + CS_Labs + Micro_Labs

subjects_df = sheets['Subjects_Weekly'].dropna(subset=['Subject'])
subject_weekly_count = dict(zip(subjects_df['Subject'].astype(str), subjects_df['Weekly_Count'].astype(int)))

units_required_map = dict(zip(subjects_df['Subject'].astype(str), subjects_df['Units_Required'].astype(int)))

faculty_df = sheets['Faculty_Map'].dropna(subset=['Subject'])
faculty_map = dict(zip(faculty_df['Subject'].astype(str), faculty_df['Faculty'].astype(str)))

MAX_CLASSES_PER_DAY = 7
sorted_slot_ids = sorted(slots.keys())

# Global trackers
shared_subject_capacity = {'PCS409': 4, 'PCS402': 2, 'PCS408': 2}
global_used_rooms = [[set() for _ in range(TOTAL_SLOTS)] for _ in range(WORKING_DAYS)]
global_used_faculty = [[set() for _ in range(TOTAL_SLOTS)] for _ in range(WORKING_DAYS)]

used_rooms = [[set() for _ in range(TOTAL_SLOTS)] for _ in range(WORKING_DAYS)]

for section in SECTIONS:
    print(f"\nGenerating timetable for Section {section}...")

    time_table = np.full((WORKING_DAYS, TOTAL_SLOTS), '', dtype=object)
    units_per_day = [0] * WORKING_DAYS
    next_free_slot = [0] * WORKING_DAYS
    daily_subjects = [set() for _ in range(WORKING_DAYS)]

    room_index = cs_lab_index = micro_lab_index = 0

    for subject, count in subject_weekly_count.items():
        units_required = units_required_map.get(subject, 1)
        scheduled = attempts = 0

        while scheduled < count and attempts < 3000:
            day = random.randint(0, WORKING_DAYS - 1)

            # Skip if this subject already scheduled today 
            if subject in daily_subjects[day]:
                attempts += 1
                continue

            # Skip if day already full
            if units_per_day[day] + units_required > MAX_CLASSES_PER_DAY:
                attempts += 1
                continue

            possible_slots = list(range(TOTAL_SLOTS - units_required + 1))
            random.shuffle(possible_slots)
            slot_found = False

            for slot in possible_slots:
                # Check if slots are empty
                if any(time_table[day][slot + offset] != '' for offset in range(units_required)):
                    continue

                # Faculty conflict
                faculty = faculty_map.get(subject)
                if faculty is None:
                    raise ValueError(f"No faculty assigned for subject '{subject}' in Faculty_Map sheet")
                if any(faculty in global_used_faculty[day][slot + offset] for offset in range(units_required)):
                    continue

                # Room assignment
                room_assigned = None

                # CS lab
                if subject in ['PCS409', 'PCS464']:
                    for lab in CS_Labs:
                        if all(lab not in used_rooms[day][slot + offset] and lab not in global_used_rooms[day][slot + offset]
                            for offset in range(units_required)):
                            room_assigned = lab
                            break

                # Micro lab
                elif subject == 'PCS403':
                    for lab in Micro_Labs:
                        if all(lab not in used_rooms[day][slot + offset] and lab not in global_used_rooms[day][slot + offset]
                            for offset in range(units_required)):
                            room_assigned = lab
                            break

                # Regular rooms
                else:
                    for room_id in room_keys:
                        room = rooms[room_id]
                        if all(room not in used_rooms[day][slot + offset] and room not in global_used_rooms[day][slot + offset]
                            for offset in range(units_required)):
                            room_assigned = room
                            break

                if room_assigned is None:
                    continue  # couldn't find room

                # Assign room to timetable
                for offset in range(units_required):
                    time_table[day][slot + offset] = f"{subject} ({room_assigned}) - {faculty}"
                    used_rooms[day][slot + offset].add(room_assigned)
                    global_used_rooms[day][slot + offset].add(room_assigned)
                    global_used_faculty[day][slot + offset].add(faculty)

                daily_subjects[day].add(subject)
                units_per_day[day] += units_required
                scheduled += 1
                slot_found = True
                break 

        if not slot_found:
            attempts += 1


    # Export to CSV
    filename = f"timetable_{section}.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Day/Slot'] + [slots[i] for i in sorted_slot_ids])
        for i in range(WORKING_DAYS):
            writer.writerow([days.get(i + 1)] + [time_table[i][slot_id - 1] for slot_id in sorted_slot_ids])

# Vacant room report
vacant_tracker = [[set(all_rooms) for _ in range(TOTAL_SLOTS)] for _ in range(WORKING_DAYS)]
for section in SECTIONS:
    with open(f"timetable_{section}.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for i, row in enumerate(reader):
            for j, entry in enumerate(row[1:], start=0):
                if '(' in entry and ')' in entry:
                    room = entry[entry.find('(')+1:entry.find(')')]
                    vacant_tracker[i][j].discard(room)

with open('vacant_classes_all_sections.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Day/Slot'] + [slots[i] for i in sorted_slot_ids])
    for i in range(WORKING_DAYS):
        row = [days.get(i + 1)]
        for j in range(TOTAL_SLOTS):
            vacant = vacant_tracker[i][j]
            row.append(', '.join(sorted(vacant)) if vacant else '---')
        writer.writerow(row)

print("Timetables and vacant report generated.")
