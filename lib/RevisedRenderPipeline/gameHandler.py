from .coordinateSystem import *
from .util import *
from .collisionShape import *
from .taskManager import ScriptScheduler
import sys
from time import ticks_ms, ticks_diff,ticks_us
from typing import TYPE_CHECKING, Set, Callable, Optional  # type: ignore
from .node import *
from .renderer import Renderer
from .coordinateSystem import VectorMapFactory

DEBUG = False
DEBUG_FPS=False

class GameHandler(Node):
  ENDING_UPDATE="GAME ENGINE ENDING UPDATE"
  BEGGINING_UPDATE="GAME ENGINE BEGGINING UPDATE"
  def __init__(self, taskmanager: ScriptScheduler, tileManager: 'Renderer', coordinateSystem: 'VectorMapFactory' = VectorMapFactory()) -> None:
    super().__init__()
    self.game_objects: Set['GameObject'] = set()
    self.taskmanager: ScriptScheduler = taskmanager
    self.tileManager: 'Renderer' = tileManager
    self.fps: int = 60
    self.backgroundColor = rgb(255, 255, 255)
    self.stopped: bool = False
    self.coordinateSystem: 'VectorMapFactory' = coordinateSystem
    self._last_frame=None
    self.delta=1000/self.fps
    # Event hooks
    self.events=taskmanager.events
    self.timers=taskmanager.timers
    self.frame_time = int(1000 / self.fps)
  def should_continue(self):
    if self.stopped:
      return False

    frame_start = ticks_ms()
    if not self._last_frame:
      self._last_frame = frame_start-self.frame_time
    self.delta = ticks_diff(frame_start, self._last_frame) / 1000.0
    
    if ticks_diff(frame_start, self._last_frame) < self.frame_time:
      if DEBUG: print("[GAMEHANDLER] skipped too little time passed")
      return False
    self._last_frame = frame_start
    if DEBUG: print(f"[GameHandler] Frame start {frame_start}, delta {self.delta:.4f}")
    return True
    
  def update(self):
    if not self.should_continue():
      return
    tot_start=ticks_ms()
    
    self.events.emit(self.BEGGINING_UPDATE)

    # Update all scripts and timers
    self.taskmanager.update(self.delta)
    
    if DEBUG: print("[GameHandler] Updating game objects")
    start=ticks_ms()

    drawActions=[]
    self.gatherDrawCalls(Vec2(0,0),drawActions)
    
    tot=f"Object time {ticks_diff(start,ticks_ms())}"
    if DEBUG_FPS:print(f"{tot:>16}")
    if DEBUG: print("[GameHandler] Drawing tiles")
    #----------------------------
    self.events.emit(self.ENDING_UPDATE)

    start=ticks_ms()
    
    self.tileManager.draw(self.backgroundColor,drawActions)

    tot=f"Render time {ticks_diff(start,ticks_ms())}"
    if DEBUG_FPS: print(f"{tot:>16}")
    tot=f"Total time {ticks_diff(tot_start,ticks_ms())}"
    if DEBUG_FPS: print(f"{tot:>16}")

  def pause(self) -> None:
      if DEBUG: print("[GameHandler] Paused")
      self.stopped = True

  def resume(self) -> None:
      if DEBUG: print("[GameHandler] Resumed")
      self.stopped = False

  def __repr__(self):
      return (f"GameHandler(fps={self.fps}, stopped={self.stopped}, "
              f"game_objects={len(self.game_objects)})")