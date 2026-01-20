import curses
import time

# ======================
# Game State Variables
# ======================
view = "CENTER"          # CENTER, LEFT, RIGHT, CAMERA
camera_up = False
current_camera = 0

left_door = False
right_door = False
left_light = False
right_light = False

power = 99               # whole number start
last_power = power
hour_timer = 0.0
game_hour_length = 85.0  # seconds per in-game hour
hour_index = 0           # internal counter
current_hour = 12        # displayed hour
dirty = True             # Flag to redraw screen

# ======================
# Global Event Variable
# ======================
last_event = "Fan noises"  # default ambient sound
event_timer = 0.0
event_duration = 5.0  # optional reset to default after X seconds

# ======================
# Camera Data
# ======================
CAM_ROOMS = [
    ("CAM 1A", "Show Stage"),
    ("CAM 1B", "Dining Area"),
    ("CAM 1C", "Pirate Cove"),
    ("CAM 2A", "Left Hall"),
    ("CAM 2B", "Left Hall Corner"),
    ("CAM 3", "Supply Closet"),
    ("CAM 4A", "Right Hall"),
    ("CAM 4B", "Right Hall Corner"),
    ("CAM 5", "Backstage"),
    ("CAM 6", "Kitchen"),
    ("CAM 7", "Restrooms")
]

CAM_KEYS = {
    ord('1'): 0,   # 1A
    ord('2'): 8,   # 5
    ord('3'): 1,   # 1B
    ord('4'): 10,  # 7
    ord('5'): 2,   # 1C
    ord('6'): 5,   # 3
    ord('7'): 6,   # 6
    ord('8'): 3,   # 2A
    ord('9'): 7,   # 4A
    ord('0'): 4,   # 2B
    ord('-'): 9    # 4B
}

# ======================
# Dialog System Variables
# ======================
dialog_queue = []       # list of strings to show
dialog_timer = 0.0      # time elapsed for current dialog
dialog_duration = 30.0  # seconds per dialog
current_dialog = ""     # currently displayed dialog

# ======================
# Dialog Update Function
# ======================
def update_dialog(delta):
    global dialog_queue, dialog_timer, current_dialog, dirty

    if dialog_queue:
        dialog_timer += delta
        if dialog_timer >= dialog_duration:
            dialog_timer = 0.0
            dialog_queue.pop(0)
            dirty = True

        if dialog_queue:
            current_dialog = dialog_queue[0]
        else:
            current_dialog = ""
            dirty = True

# ======================
# Draw Function
# ======================
def draw(stdscr):
    stdscr.clear()

    # Event bar at top
    stdscr.addstr(0, 0, f"Last Sound: {last_event}")

    # Power + Bar + Time on same line
    active_count = sum([left_door, right_door, left_light, right_light, camera_up])
    bars = min(active_count + 1, 4)
    power_str = f"Power: {int(power)}% "
    bar_str = "[" + "|"*bars + " "*(4-bars) + "]"
    time_str = f"  Time: {current_hour}AM"
    stdscr.addstr(1, 0, power_str + bar_str + time_str)

    # View indicator
    stdscr.addstr(2, 0, f"View: {view}")
    base_row = 3

    # If in camera mode, show camera info below the view
    if camera_up:
        cam_id, cam_name = CAM_ROOMS[current_camera]
        stdscr.addstr(base_row, 0, f"{cam_id}: {cam_name}")
        stdscr.addstr(base_row+1, 0, "Switch Camera: 1 2 3 4 5 6 7 8 9 0 -")
        base_row += 2

    # Doors / Lights
    stdscr.addstr(base_row, 0, f"Left Door: {'Closed' if left_door else 'Open'}  Light: {'On' if left_light else 'Off'}")
    stdscr.addstr(base_row+1, 0, f"Right Door: {'Closed' if right_door else 'Open'}  Light: {'On' if right_light else 'Off'}")

    # Controls
    stdscr.addstr(base_row+2, 0, "Controls:")
    stdscr.addstr(base_row+3, 0, "  A - Look LEFT")
    stdscr.addstr(base_row+4, 0, "  D - Look RIGHT")
    if view in ["LEFT", "RIGHT"]:
        stdscr.addstr(base_row+5, 0, "  E - Close the door on this side")
        stdscr.addstr(base_row+6, 0, "  R - Toggle light on this side")
        controls_row = base_row+7
    else:
        controls_row = base_row+5

    if view == "CENTER":
        stdscr.addstr(controls_row, 0, "  W - Open camera")
        controls_row += 1
    if camera_up:
        stdscr.addstr(controls_row, 0, "  S - Exit camera")
    else:
        stdscr.addstr(controls_row, 0, "  S - Return to CENTER")
    stdscr.addstr(controls_row+1, 0, "  Q - Quit")

    # Dialog Box at bottom
    if current_dialog:
        height, width = stdscr.getmaxyx()
        dialog_str = f"[DIALOG] {current_dialog}"
        stdscr.addstr(height - 2, 0, dialog_str[:width-1])

    stdscr.refresh()

# ======================
# Main Loop
# ======================
def main(stdscr):
    global view, camera_up, current_camera
    global left_door, right_door, left_light, right_light
    global power, last_power, hour_timer, current_hour, hour_index
    global last_event, event_timer, dirty

    curses.curs_set(0)
    stdscr.nodelay(True)
    last_time = time.time()

    # Filler dialog
    dialog_queue.extend([
        "Welcome to the Night Shift!",
        "Your job: survive until 6AM.",
        "Check the cameras often, but conserve power.",
        "Don't forget to close doors if you see anything suspicious!",
        "Good luck!"
    ])

    while True:
        now = time.time()
        delta = now - last_time
        last_time = now

        # ======================
        # Hour tracking using index
        # ======================
        hour_timer += delta
        if hour_timer >= game_hour_length:
            hour_timer -= game_hour_length
            hour_index += 1
            current_hour = 12 if hour_index == 0 else hour_index
            dirty = True

            # Win condition at 6AM
            if current_hour == 6:
                dialog_queue.append("Congratulations! You survived the night!")
                break

        # ======================
        # Power drain
        # ======================
        active_count = sum([left_door, right_door, left_light, right_light, camera_up])
        if active_count == 0: power_drain_per_sec = 0.141
        elif active_count == 1: power_drain_per_sec = 0.235
        elif active_count in [2,3]: power_drain_per_sec = 0.341
        else: power_drain_per_sec = 0.447

        power -= power_drain_per_sec * delta
        if power < 0: power = 0
        if int(power) != int(last_power):
            dirty = True
            last_power = power

        # ======================
        # Event reset timer
        # ======================
        event_timer += delta
        if event_timer >= event_duration:
            last_event = "Fan noises"
            event_timer = 0.0
            dirty = True

        # ======================
        # Update dialog
        # ======================
        update_dialog(delta)

        # ======================
        # Input handling
        # ======================
        key = stdscr.getch()
        if key != -1:
            if key == ord('q'): break

            if camera_up:
                if key in CAM_KEYS:
                    current_camera = CAM_KEYS[key]
                    last_event = f"Camera {current_camera+1} activated"
                    event_timer = 0.0
                    dirty = True
                elif key == ord('s'):
                    camera_up = False
                    view = "CENTER"
                    dirty = True
            else:
                if key == ord('a'):
                    view = "LEFT"
                    dirty = True
                    last_event = "Footsteps heard on left"
                    event_timer = 0.0
                elif key == ord('d'):
                    view = "RIGHT"
                    dirty = True
                    last_event = "Footsteps heard on right"
                    event_timer = 0.0
                elif key == ord('e'):
                    if view == "LEFT": left_door = not left_door
                    if view == "RIGHT": right_door = not right_door
                    dirty = True
                    last_event = "Door toggled"
                    event_timer = 0.0
                elif key == ord('r'):
                    if view == "LEFT": left_light = not left_light
                    if view == "RIGHT": right_light = not right_light
                    dirty = True
                    last_event = "Light toggled"
                    event_timer = 0.0
                elif key == ord('w') and view == "CENTER":
                    camera_up = True
                    view = "CAMERA"
                    current_camera = 0
                    dirty = True
                elif key == ord('s'):
                    view = "CENTER"
                    dirty = True

        # ======================
        # Redraw if needed
        # ======================
        if dirty:
            draw(stdscr)
            dirty = False

        time.sleep(0.05)

# ======================
# Run the game
# ======================
curses.wrapper(main)
