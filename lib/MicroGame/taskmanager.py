if __name__ == "__main__":
    from typing import Callable

class Task:
    def __init__(self,action,tag=None):
        self.action=action
        self.tag=tag
    
    def step(self):
        return next(self.action)
    
class TaskManager:
    def __init__(self):
        self.tasks=[]
        self.dt=0
    
    def update(self):
        task:Task
        for task in self.tasks[:]:
            try:
                task.step()
            except StopIteration:
                self.tasks.remove(task)

    def add(self, task_or_func,tag=""):
        """Add either a Task, a generator, or a generator function (will be auto-wrapped)."""
        if isinstance(task_or_func, Task):
            self.tasks.append(task_or_func)

        elif hasattr(task_or_func, '__next__') and hasattr(task_or_func, '__iter__'):
            self.tasks.append(Task(task_or_func, tag))

        elif callable(task_or_func):
            # If they accidentally passed a function, not generator — warn or run
            gen = task_or_func()
            if hasattr(gen, '__next__') and hasattr(gen, '__iter__'):
                raise TypeError("Function must return a generator")
            self.tasks.append(Task(gen, tag))

        else:
            raise TypeError("TaskManager.add() expected a Task, generator, or generator function")
    
    def cancel_tag(self,tag):
        self.tasks = [t for t in self.tasks if t.tag!=tag]

    def wait(self,seconds):
            """Väntar sekunder innan den går vidare, skriv *yield from*!
            Exempel: yield from game.taskmanager.wait(3)"""
            elapsed=0
            while elapsed<seconds:
                yield
                elapsed+=self.dt # type: ignore


    def wait_until(self,condition_fn:Callable):
            while not condition_fn():
                yield



    def repeat(self,times,action):
        for _ in range(times):
            action()
            yield