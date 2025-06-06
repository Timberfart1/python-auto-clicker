import turtle
import ctypes
import ctypes.wintypes
import threading
import time
import os

# --- Windows mouse click via ctypes ---
SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)
class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]
class Input_I(ctypes.Union):
    _fields_ = [("mi", MouseInput)]
class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]
def click_mouse():
    # Mouse left button down and up
    SendInput(1, ctypes.byref(Input(0, Input_I(MouseInput(0,0,0,0x0002,0,None)))), ctypes.sizeof(Input))
    SendInput(1, ctypes.byref(Input(0, Input_I(MouseInput(0,0,0,0x0004,0,None)))), ctypes.sizeof(Input))

# --- Globals ---
clicking = False
delay = 0.1  # seconds per click
status_msg = "Ready"
save_file = "auto_clicker_settings.txt"
bg_dark = True
bg_colors = {True:"#1E1E1E", False:"#F0F0F0"}
fg_colors = {True:"white", False:"black"}

# --- Save/load settings ---
def save_settings():
    try:
        with open(save_file, "w") as f:
            f.write(f"{bg_dark}\n{delay}\n")
    except:
        pass

def load_settings():
    global bg_dark, delay
    if os.path.exists(save_file):
        try:
            with open(save_file) as f:
                b,d = f.read().splitlines()[:2]
                bg_dark = (b=="True")
                delay = max(float(d), 0.001)
        except:
            pass

# --- Clicking thread ---
def click_loop():
    global clicking, delay
    while clicking:
        click_mouse()
        time.sleep(delay)

# --- Turtle UI setup ---
screen = turtle.Screen()
screen.title("Auto Clicker with Buttons")
screen.setup(700, 550)
screen.bgcolor(bg_colors[bg_dark])
screen.tracer(0)
pen = turtle.Turtle()
pen.hideturtle()
pen.penup()

BUTTON_W, BUTTON_H, GAP_Y = 180, 60, 30
START_X, START_Y = -300, 210

def draw_button(x, y, text, fill="#4CAF50"):
    pen.goto(x, y)
    pen.color("black", fill)
    pen.pensize(1)
    pen.begin_fill()
    for _ in range(2):
        pen.forward(BUTTON_W)
        pen.right(90)
        pen.forward(BUTTON_H)
        pen.right(90)
    pen.end_fill()
    # Draw thick border
    pen.pensize(4)
    pen.color("black")
    pen.goto(x, y)
    for _ in range(2):
        pen.forward(BUTTON_W)
        pen.right(90)
        pen.forward(BUTTON_H)
        pen.right(90)
    pen.pensize(1)
    # Write text
    pen.goto(x + 15, y - BUTTON_H + 25)
    pen.color("white" if fill != "white" else "black")
    pen.write(text, font=("Arial", 18, "bold"))

def draw_label(x, y, text, size=16, color=None):
    pen.goto(x, y)
    pen.color(color or fg_colors[bg_dark])
    pen.write(text, font=("Arial", size, "normal"))

def draw_ui():
    pen.clear()
    # Title
    pen.goto(-220, 270)
    pen.color(fg_colors[bg_dark])
    pen.write("🖱️ Auto Clicker with Buttons", font=("Arial", 32, "bold"))

    # CPS Label and Set CPS button
    cps_val = round(1 / delay)
    draw_label(START_X, START_Y, f"Clicks Per Second (1 - 1000): {cps_val}", 20)
    draw_button(START_X + 380, START_Y + 10, "Set CPS", fill="#2196F3")

    # Mode Label and Toggle Mode button
    mode_text = "Dark Mode" if bg_dark else "Light Mode"
    draw_label(START_X, START_Y - 2 * (BUTTON_H + GAP_Y), f"Current Mode: {mode_text}", 20)
    draw_button(START_X + 380, START_Y - 2 * (BUTTON_H + GAP_Y) + 10, "Toggle Mode", fill="#9C27B0")

    # Start and Stop buttons
    draw_button(START_X + 380, START_Y - 4 * (BUTTON_H + GAP_Y) + 10, "Start Clicking", fill="#4CAF50")
    draw_button(START_X + 380, START_Y - 5 * (BUTTON_H + GAP_Y) + 10, "Stop Clicking", fill="#F44336")

    # Status message
    draw_label(-320, -230, f"Status: {status_msg}", 18)

    screen.update()

def inside_box(x, y, bx, by):
    return bx <= x <= bx + BUTTON_W and by - BUTTON_H <= y <= by

# --- Button actions ---
def prompt_cps():
    global delay, status_msg
    ans = screen.textinput("Set CPS", "Enter CPS (1 - 10000):")
    if ans:
        try:
            v = float(ans)
            if 1 <= v <= 10000:
                delay = 1 / v
                status_msg = f"CPS set to {round(v)}"
            else:
                status_msg = "CPS must be between 1 and 10000!"
        except:
            status_msg = "Invalid CPS input!"
    else:
        status_msg = "CPS change cancelled"
    draw_ui()

def toggle_mode():
    global bg_dark, status_msg
    bg_dark = not bg_dark
    screen.bgcolor(bg_colors[bg_dark])
    status_msg = "Switched to " + ("Dark Mode" if bg_dark else "Light Mode")
    draw_ui()

def delayed_start():
    global clicking, status_msg
    for i in range(5, 0, -1):
        status_msg = f"Starting in {i}..."
        draw_ui()
        time.sleep(1)
        if not clicking:
            status_msg = "Start cancelled."
            draw_ui()
            return
    if clicking:
        status_msg = "Clicking started!"
        draw_ui()
        click_loop()

def start_clicking():
    global clicking, status_msg
    if not clicking:
        clicking = True
        threading.Thread(target=delayed_start, daemon=True).start()

def stop_clicking():
    global clicking, status_msg
    if clicking:
        clicking = False
        status_msg = "Clicking stopped."
        draw_ui()

def on_click(x, y):
    if inside_box(x, y, START_X + 380, START_Y + 10):
        prompt_cps()
    elif inside_box(x, y, START_X + 380, START_Y - 2 * (BUTTON_H + GAP_Y) + 10):
        toggle_mode()
    elif inside_box(x, y, START_X + 380, START_Y - 4 * (BUTTON_H + GAP_Y) + 10):
        start_clicking()
    elif inside_box(x, y, START_X + 380, START_Y - 5 * (BUTTON_H + GAP_Y) + 10):
        stop_clicking()

screen.onclick(on_click)

# --- Program start ---
load_settings()
screen.bgcolor(bg_colors[bg_dark])
draw_ui()

# Save settings on window close
def save_and_exit():
    save_settings()
    turtle.bye()
screen.getcanvas().winfo_toplevel().protocol("WM_DELETE_WINDOW", save_and_exit)

turtle.done()
