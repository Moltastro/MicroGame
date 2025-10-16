import time

# --- Scheduler ---
class ScriptScheduler:
    def __init__(self):
        self.scripts = []
        
        self.events = EventBus()
        self.timers = TimerManager()

    def start(self, gen_or_func, name=None):
        # Allow passing either a generator or a function that returns one
        if callable(gen_or_func) and not hasattr(gen_or_func, "__next__"):
            gen = gen_or_func()  # call it to get the generator
        else:
            gen = gen_or_func

        if not hasattr(gen, "__next__"):
            raise TypeError(f"{gen_or_func} is not a generator or generator function")

        self.scripts.append({"gen": gen, "name": name})


    def stop(self, name):
        self.scripts = [s for s in self.scripts if s["name"] != name]

    def update(self, delta):
        # Update running scripts
        for s in self.scripts[:]:
            try:
                next(s["gen"])
            except StopIteration:
                self.scripts.remove(s)
        # Update timers
        self.timers.update(delta)

# --- Event System ---
class EventBus:
    def __init__(self):
        self.listeners = {}

    def on(self, event, callback):
        self.listeners.setdefault(event, []).append(callback)

    def emit(self, event, *args, **kwargs):
        for cb in self.listeners.get(event, []):
            cb(*args, **kwargs)

# --- Timer Manager ---
class TimerManager:
    def __init__(self):
        self.timers = []

    def after(self, seconds, callback):
        self.timers.append({"time": seconds, "repeat": False, "callback": callback})

    def every(self, seconds, callback):
        self.timers.append({"time": seconds, "repeat": True, "callback": callback, "period": seconds})

    def update(self, delta):
        for t in self.timers[:]:
            t["time"] -= delta
            if t["time"] <= 0:
                t["callback"]()
                if t.get("repeat"):
                    t["time"] += t["period"]
                else:
                    self.timers.remove(t)

# --- Script Helpers ---
def frames(count, yielder=lambda:None):
    for i in range(count):
        yielder()
        yield i

def wait(seconds, yielder=lambda:None):
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < seconds * 1000:
        yielder()
        yield

def wait_until(condition, yielder=lambda:None):
    while not condition():
        yielder()
        yield
def script(func):
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        if not hasattr(gen, '__next__'):
            raise TypeError("@script must decorate a generator function")
        return gen
    return wrapper


def forever(func):
    def wrapper(*args, **kwargs):
        def loop():
            while True:
                sub = func(*args, **kwargs)
                if not hasattr(sub, '__next__'):
                    raise TypeError("@forever must decorate a generator function")
                yield from sub
        return loop()
    return wrapper



if __name__=="__main__":
    # --- Example Usage ---
    class Player:
        def __init__(self):
            self.x = 0
        def move(self, dx):
            self.x += dx
            print(f"[PLAYER] x={self.x:.1f}")

    player = Player()
    scheduler = ScriptScheduler()

    @script
    def move_until_hit():
        print("[SCRIPT] Waiting for 'hit' event...")
        yield from wait_until(lambda: hasattr(player, "hit"), lambda: None)
        print("[SCRIPT] Player was hit! Moving back 10...")
        for i in frames(10, lambda: None):
            player.move(-1)
            yield

    # Register a timer that emits event after 1s
    scheduler.timers.after(1.0, lambda: scheduler.events.emit("hit"))

    # Event listener that sets a flag
    scheduler.events.on("hit", lambda: setattr(player, "hit", True))

    # Start script
    scheduler.start(move_until_hit(), name="move_back")

    # --- Game Loop ---
    last = time.ticks_ms()
    while scheduler.scripts or scheduler.timers.timers:
        now = time.ticks_ms()
        delta = time.ticks_diff(now, last) / 1000.0
        last = now
        scheduler.update(delta)
        time.sleep(0.05)
