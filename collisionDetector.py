import random
import numpy as np

rooms = {
    1: '101', 2: '102', 3: '103', 4: '104', 5: '105', 6: '106',
    7: '201', 8: '202', 9: '203', 10: '204', 11: '205', 12: '206', 13: '207',
    14: '301'
}

slots = {
    1:'8:00-8:55', 2: '8:55-9:50', 3: '10:10-11:05', 4:'11:05-12:00', 5:'12:00-12:55', 6:'12:55-1:50', 7:'2:10-3:05', 8:'3:05-4:00', 9:'4:00-4:55', 10:'4:55-5:50'
}

# This is only for a single day
colMatrix = np.zeros((len(rooms), len(slots)), dtype=int)

maxClass = 5
totalSec = 24
extra, i = 0, 0

while i < (maxClass * totalSec + extra):
    room = random.randint(0, len(rooms) - 1)
    slot = random.randint(0, len(slots) - 1)
    if colMatrix[room][slot] != 1:
        colMatrix[room][slot] = 1
    else:
        extra += 1
    i += 1

elements, frequency = np.unique(colMatrix, return_counts= True)

print(colMatrix)
print(elements, frequency, extra)

CORE_SEC_DATA={0:'A1',1:'A2',2:'B1',3:'B2',4:'C1',5:'C2',6:'D1',7:'D2',8:'E1',9:'E2',10:'F1',11:'F2',12:'G1',13:'G2',14:'H1',15:'H2',16:'I1'}
AI_ML_SEC_DATA={0:'K1',1:'K2',2:'L1',3:'L2'}
AI_DS_SEC_DATA={0:'J1',1:'J2'}
CBS_SEC_DATA={0:'I2'}

