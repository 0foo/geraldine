
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



    def get_watcher_handler(source_dir):
    from watchdog.events import FileSystemEventHandler

    class MyEventHandler(FileSystemEventHandler):
        def __init__(self, observer):
            self.observer = observer
        def run(self):
            command = "geri"
            directory = os.path.dirname(source_dir)
            result = subprocess.run(command, shell=True, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                print(f"{result.stdout}")
            else:
                print(f"Error in executing geri command:\n{result.stderr}")
        def on_any_event(self, event):
            print(f"Event detected: {event}")
            if event.event_type == "opened":
                return
            if event.event_type == "closed":
                return
            try:
                self.run()
            except Exception as e:
                print(e)
            self.observer.stop()  # Stop after the first event
    return MyEventHandler
    

def watcher(directory_to_watch, file_system_event_handler):
    import time
    from watchdog.observers import Observer

    class DirectoryWatcher:
        def __init__(self):
            self.observer = Observer()

        def run_once(self):
            self.observer.schedule(file_system_event_handler(self.observer), directory_to_watch, recursive=True)
            self.observer.start()
            # print(f"Started watching directory: {directory_to_watch}. Waiting for a single event.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping directory watcher...")
            finally:
                self.observer.stop()
                self.observer.join()
    watcher = DirectoryWatcher()
    watcher.run_once()
    

    # def get_simple_server(directory, port=8000):
#     import http.server
#     import socketserver
#     import threading
#     import os
#     import requests

#     class SimpleServer:
#         def __init__(self, port, directory=None):
#             self.port = port
#             self.directory = directory
#             self.is_running = False
#             self.httpd = None
#             self.thread = None

#         def start_server(self):
#             if self.directory:
#                 os.chdir(self.directory)

#             # Create an HTTP request handler
#             handler = http.server.SimpleHTTPRequestHandler

#             # Create the HTTP server
#             self.httpd = socketserver.TCPServer(("", self.port), handler)

#             # Use a flag to control the loop
#             self.is_running = True
#             self.thread = threading.Thread(target=self.run_server)
#             self.thread.start()
#             print(f"Serving from directory root: {os.getcwd()}")
#             print(f"Starting HTTP server at http://localhost:{self.port}")

#         def run_server(self):
#             while self.is_running:
#                 self.httpd.handle_request()

#         def stop_server(self):
#             self.is_running = False
#             self.httpd.server_close()
#             self.thread.join()
#             print("Server stopped.")

#         def stop_server(self):
#             self.is_running = False

#             # Send a dummy request to the server to unblock handle_request
#             try:
#                 requests.get(f"http://localhost:{self.port}")
#             except requests.RequestException:
#                 pass  # Ignore request errors, as the server might close before handling it

#             self.httpd.server_close()
#             self.thread.join()
#             print("Server stopped.")

#     return SimpleServer(port, directory) 


# def start_simple_server(port=8000, directory=None):
#     import http.server
#     import socketserver
    
#     class ReusableTCPServer(socketserver.TCPServer):
#         allow_reuse_address = True

#     if directory:
#         os.chdir(directory)
 
#     directory = os.getcwd()


#     # Create an HTTP request handler
#     handler = http.server.SimpleHTTPRequestHandler

#     # Create the HTTP server with ReusableTCPServer
#     with ReusableTCPServer(("", port), handler) as httpd:
#         print(f"\nServing from directory root: {os.getcwd()}")
#         print(f"Starting HTTP server at http://localhost:{port}")
#         httpd.serve_forever()