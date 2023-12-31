
def get_watcher_handler(source_dir):
    class MyHandler(FileSystemEventHandler):
            def __init__(self):
                self.last_handled_time = 0
                self.delay = 1
            def should_handle_event(self):
                current_time = time.time()
                if current_time - self.last_handled_time > self.delay:
                    self.last_handled_time = current_time
                    return True
                return False
            def run(self):
                command = "geri"
                directory = os.path.dirname(source_dir)
                result = subprocess.run(command, shell=True, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    print(f"{result.stdout}")
                else:
                    print(f"Error in executing geri command:\n{result.stderr}")
            def on_any_event(self, event):
                if not self.should_handle_event():  
                    return
                if event.event_type == "opened":
                    return
                if event.event_type == "closed":
                    return
                print()
                print(event)
                self.run()
    return MyHandler




def watcher(directory_to_watch, file_system_event_handler):
    import time
    from watchdog.observers import Observer
    
    class DirectoryWatcher:
        def __init__(self, directory_to_watch):
            self.observer = Observer()
            self.directory_to_watch = directory_to_watch

        def run(self):
            event_handler = file_system_event_handler()
            self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
            self.observer.start()
            print(f"\nStarted watching directory: {directory_to_watch}. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping directory watcher...")
                self.observer.stop()

            self.observer.join()

    watcher = DirectoryWatcher(directory_to_watch)
    watcher.run()