import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import time

# ---------------- CONFIG ----------------
HOUR_DURATION = 90.0
FRAME_RATE = 10
HOUR_LABELS = ["12 AM", "1 AM", "2 AM", "3 AM", "4 AM", "5 AM", "6 AM"]

# ---------------- INIT ----------------
pygame.init()
pygame.display.set_mode((1, 1))
clock = pygame.time.Clock()

# ---------------- STATE ----------------
state = {
    "running": True,
    "power": 100.0,
    "left_door": False,
    "right_door": False,
    "camera": "Office",
    "events": [],
    "hour": 0,
}

last_power = 100
last_hour = 0

# ---------------- UTILS ----------------
def clear_screen():
    print("\033[2J\033[H", end="", flush=True)

def render():
    clear_screen()
    print("PNAF — CLI EDITION")
    print(f"Time: {HOUR_LABELS[state['hour']]}")
    print()
    print(f"Power: {int(state['power'])}%")
    print(f"Doors: L {'CLOSED' if state['left_door'] else 'OPEN'} | "
          f"R {'CLOSED' if state['right_door'] else 'OPEN'}")
    print(f"Camera: {state['camera']}")
    print()
    print("Events:")
    if state["events"]:
        for e in state["events"][-5:]:
            print(f" - {e}")
        state["events"].clear()
    else:
        print(" - Nothing.")
    print()
    print("A/D = Doors | W = Cameras | S = Office | Q = Quit")

# ---------------- GAME LOGIC ----------------
def update_power(mult):
    global last_power
    drain = 0.02 * mult
    if state["left_door"]:
        drain += 0.05
    if state["right_door"]:
        drain += 0.05

    state["power"] = max(0, state["power"] - drain)
    if int(state["power"]) != last_power:
        last_power = int(state["power"])
        render()

    if state["power"] <= 0:
        state["events"].append("The power has gone out.")
        render()
        state["running"] = False

def handle_input():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                state["left_door"] = not state["left_door"]
                render()
            elif event.key == pygame.K_d:
                state["right_door"] = not state["right_door"]
                render()
            elif event.key == pygame.K_w:
                state["camera"] = "Cameras"
                render()
            elif event.key == pygame.K_s:
                state["camera"] = "Office"
                render()
            elif event.key == pygame.K_q:
                state["running"] = False

# ---------------- MAIN LOOP ----------------
def main():
    global last_hour
    start_time = time.monotonic()
    render()

    while state["running"]:
        clock.tick(FRAME_RATE)

        elapsed = time.monotonic() - start_time
        hour = min(int(elapsed // HOUR_DURATION), 5)

        if hour != last_hour:
            last_hour = hour
            state["hour"] = hour
            state["events"].append(HOUR_LABELS[hour])
            render()

        difficulty = 1.0 + hour * 0.25
        update_power(difficulty)
        handle_input()

    clear_screen()
    print("GAME OVER")

if __name__ == "__main__":
    main()
