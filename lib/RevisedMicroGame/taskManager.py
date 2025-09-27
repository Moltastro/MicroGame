import time
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

# --- Wait helpers ---
def wait(seconds):
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < seconds * 1000:
        yield

def wait_until(condition):
    while not condition():
        yield

def script(func):
    """Decorator that turns a normal function into a resumable generator."""
    def wrapper(*args, **kwargs):
        def runner():
            yield from func(*args, **kwargs)
        return runner()
    return wrapper

if __name__=="__main__":
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
            yield from wait(0.1)  # wait 0.1s between moves
        print("[UPDATE] Done moving!")

    @script
    def remove_outside_screen():
        yield from wait_until(lambda: player.x < 0)
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

        frame += 1
        scheduler.update()
        time.sleep(0.05)  # Simulate frame time
        if frame > 200:  # Safety break
            print("Timeout!")
            break

    print("Game loop finished.")
