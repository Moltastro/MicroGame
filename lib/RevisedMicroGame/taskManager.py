import time
import contextvars
from machine import Pin
from picozero import Button
# --- Task Scheduler ---
class ScriptScheduler:
    def __init__(self):
        self.scripts = []

    def add(self, gen):
        self.scripts.append(gen)

    def update(self):
        for gen in self.scripts[:]:
            try:
                next(gen)
            except StopIteration:
                self.scripts.remove(gen)

# --- Magic Context for Pausing ---
_current_yielder = contextvars.ContextVar("_current_yielder")

def wait(seconds):
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < seconds * 1000:
        _current_yielder.get()()  # causes yield
    # when loop finishes, function resumes

def wait_until(condition):
    while not condition():
        _current_yielder.get()()  # causes yield

def script(func):
    """Decorator that turns a normal function into a resumable generator."""
    def wrapper(*args, **kwargs):
        def runner():
            def do_yield():
                yield  # <-- this makes runner a generator
            token = _current_yielder.set(lambda: (yield))
            try:
                func(*args, **kwargs)
            finally:
                _current_yielder.reset(token)
        return runner()
    return wrapper

# --- Example Game Objects ---
class Player:
    def __init__(self):
        self.x = 10
        self.removed = False

    def move(self, dx, dy):
        self.x += dx
        print(f"[MOVE] Player at x={self.x}")

    def remove(self):
        self.removed = True
        print("[REMOVE] Player removed!")

player = Player()

# --- Scripts using EXACT Syntax ---
@script
def update():
    # Move left 1 step every frame for 5 frames
    for _ in range(5):
        player.move(-1, 0)
        wait(0.1)  # wait 0.1s between moves
    print("[UPDATE] Done moving!")

@script
def remove_outside_screen():
    wait_until(lambda: player.x < 0)
    player.remove()

# --- Main Loop Simulation ---
scheduler = ScriptScheduler()
scheduler.add(update())
scheduler.add(remove_outside_screen())

frame = 0
while scheduler.scripts:
    frame += 1
    scheduler.update()
    time.sleep(0.05)  # Simulate frame time
    if frame > 200:  # Safety break
        print("Timeout!")
        break

print("Game loop finished.")
