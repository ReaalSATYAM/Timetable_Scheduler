import random
import numpy as np

WORKING_DAYS = 5
TOTAL_SLOTS = 10
MAX_CLASSES_PER_DAY = 8

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
    'PESE400':1
}

time_table = np.full((WORKING_DAYS, TOTAL_SLOTS), '', dtype=object)
units_per_day = [0] * WORKING_DAYS
next_free_slot = [0] * WORKING_DAYS

for subject, count in subject_weekly_count.items():
    if subject.startswith('P') or subject == 'TCS409':
        units_required = 2
    else:
        units_required = 1
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

        for offset in range(units_required):
            time_table[day][slot + offset] = subject

        next_free_slot[day] += units_required
        units_per_day[day] += units_required

print("\n🗓️ Compact Timetable :\n")
for i, row in enumerate(time_table):
    print(f"Day {i + 1}: {row}")
