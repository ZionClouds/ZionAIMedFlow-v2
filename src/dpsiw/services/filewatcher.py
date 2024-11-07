from time import sleep
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler


class WatchdogEventHandler(FileSystemEventHandler):
    def __init__(self, delegate):
        self.delegate = delegate

    def on_created(self, event: FileSystemEvent) -> None:
        if self.delegate:
            self.delegate(event.src_path)
    # def on_any_event(self, event):
    #     print(event)


def watch_folder(folder: str = ".", delegate=None):
    """
    Watch a folder for changes
    """
    event_handler = WatchdogEventHandler(delegate)
    observer = Observer()
    folder = "."
    print(f"Watching changes in folder {folder}")
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    try:
        while True:
            sleep(1)
    finally:
        observer.stop()
        observer.join()
