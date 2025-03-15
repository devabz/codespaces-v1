import math
from src.time_base_seconds import TimeUnits

# Room dimensions
H_Room_Low: float = 0.7
H_Room_Top: float = 3.7
L_Room: float = 6.0
B_Room: float = 4.0

V_ROOM: float = L_Room * B_Room * (H_Room_Low + H_Room_Top) / 2  # Room volume
A_ROOF: float = 2 * L_Room * math.sqrt(2) * (H_Room_Top - H_Room_Low)  # Root area
A_WALL: float = 2 * B_Room * (H_Room_Low + H_Room_Top) * math.sqrt(2)  # Wall area, denne stemmer ikke med side 40
#A_WALL: float = 2 * L_Room * H_Room_Low + B_Room * (H_Room_Top + H_Room_Low)  # Wall area
A_WINDOW: float = 1.0 * 1.4  # Window area
A_RADIATOR: float = 4  # Raditator area
V_RADIATOR: float = 10  # Raditator Volume

V_RADIATOR_WATER: float = 10.0
P_RADIATOR: float = 500

D_WATER: float = 1  # Density water
C_WATER: float = 4.19 * 1000  # Heat capacity

D_AIR: float = 1.204  # Density air
C_AIR: float = 1.009 * 1000  # Heat capacity

F_WATER: float = 125 / TimeUnits.hour  # Flow of water

K_RADIATOR: float = 30 / TimeUnits.second  # Uhe - Radiator transfer coefficient
K_WALL: float = 0.20 / TimeUnits.second  # Uwa - Wall heat transfer coefficient
K_ROOF: float = 0.15 / TimeUnits.second  # Uro - Roof heat transfer coefficient
K_OPEN_WINDOW: float = 10 / TimeUnits.second  # Uwi_open Open window heat transfer coefficient
K_CLOSED_WINDOW: float = 1.2 / TimeUnits.second  # Uwi_closed Closed window heat transfer coefficient

# Access using .notation as in U.wa gives access to the K_WALL heat transfer coefficient
class U:
    he = K_RADIATOR
    wa = K_WALL
    ro = K_ROOF
    wi_open = K_OPEN_WINDOW
    wi_closed = K_CLOSED_WINDOW