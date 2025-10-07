from .coordinateSystem import *
from .util import *
from .collisionShape import *
from .taskManager import ScriptScheduler
from time import ticks_ms, ticks_diff
from typing import TYPE_CHECKING, Set, Callable, Optional  # type: ignore
if TYPE_CHECKING:
    from .gameObject import GameObject
    from .tileManager import TileManager
    from .coordinateSystem import VectorMapFactory

DEBUG = False

class GameHandler:
    ENDING_UPDATE="GAME ENGINE ENDING UPDATE"
    BEGGINING_UPDATE="GAME ENGINE BEGGINING UPDATE"
    def __init__(self, taskmanager: ScriptScheduler, tileManager: 'TileManager', coordinateSystem: 'VectorMapFactory' = VectorMapFactory()) -> None:
        self.game_objects: Set['GameObject'] = set()
        self.taskmanager: ScriptScheduler = taskmanager
        self.tileManager: 'TileManager' = tileManager
        self.fps: int = 30
        self.backgroundColor = rgb(255, 255, 255)
        self.stopped: bool = False
        self.coordinateSystem: 'VectorMapFactory' = coordinateSystem
        self._last_frame=None
        # Event hooks
        self.events=taskmanager.events
        self.timers=taskmanager.timers

    def update(self):
        if self.stopped:
            if DEBUG: print("[GameHandler] Update skipped (paused)")
            return

        frame_start = ticks_ms()
        if not self._last_frame:
            self._last_frame = frame_start
        delta = ticks_diff(frame_start, self._last_frame) / 1000.0

        frame_time = int(1000 / self.fps)
        if ticks_diff(frame_start, self._last_frame) < frame_time:
            return  # Not enough time has passed, skip this frame

        self._last_frame = frame_start

        self.events.emit(self.BEGGINING_UPDATE)

        # Update all scripts and timers
        self.taskmanager.update(delta)

        if DEBUG: print(f"[GameHandler] Frame start {frame_start}, delta {delta:.4f}")
        if DEBUG: print("[GameHandler] Updating game objects")
        for obj in self.game_objects:
            obj.update(delta, self.tileManager, self.coordinateSystem)
        
        if DEBUG: print("[GameHandler] Drawing tiles")
        self.events.emit(self.ENDING_UPDATE)
        print(type(self.tileManager))
        self.tileManager.draw(self.coordinateSystem,self.backgroundColor)

    def add(self, gameObject: 'GameObject') -> None:
        if DEBUG: print(f"[GameHandler] Adding game object {gameObject}")
        self.game_objects.add(gameObject)

    def remove(self, gameObject: 'GameObject') -> None:
        if DEBUG: print(f"[GameHandler] Removing game object {gameObject}")
        self.game_objects.discard(gameObject)

    def pause(self) -> None:
        if DEBUG: print("[GameHandler] Paused")
        self.stopped = True

    def resume(self) -> None:
        if DEBUG: print("[GameHandler] Resumed")
        self.stopped = False

    def __repr__(self):
        return (f"GameHandler(fps={self.fps}, stopped={self.stopped}, "
                f"game_objects={len(self.game_objects)})")