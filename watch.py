import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import zipfile

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print("New file detected")
            time.sleep(5)
            print(f"New file created: {event.src_path}")
            if event.src_path.endswith('.zip'):
                # Check integrity of the zip file
                with zipfile.ZipFile(event.src_path, 'r') as myzip:
                    corrupt_file = myzip.testzip()
                    if corrupt_file is not None:
                        print(f"Corrupted file detected in the zip: {corrupt_file}")
                        return

                # move the file
                new_path = f"C:/Users/user/Desktop/capstone/instant-ngp/{os.path.basename(event.src_path)}"
                shutil.move(event.src_path, new_path)
                print(f"Moved: {event.src_path} -> {new_path}")

                # Unzip
                shutil.unpack_archive(new_path, f"C:/Users/user/Desktop/capstone/instant-ngp/")
                print(f"Unzipped: {new_path}")

                time.sleep(5)
                # Remove the zip file
                os.remove(new_path)
                print(f"Removed: {new_path}")

                # Folder name (without extension)
                folder_name = os.path.splitext(os.path.basename(new_path))[0]
                folder_path = f"C:/Users/user/Desktop/capstone/instant-ngp/{folder_name}"

                subprocess.run(["python","C:/Users/user/Desktop/capstone/instant-ngp/scripts/SAM_Remove_Background.py",folder_path+"/images"])
                subprocess.run(["python", "C:/Users/user/Desktop/capstone/instant-ngp/scripts/colmap2nerf.py", "--images", folder_path+"/images_OUTPUT", "--run_colmap", "--out", folder_path + "/" + folder_name + ".json"], input="y\n", text=True)
                subprocess.run(["python", "C:/Users/user/Desktop/capstone/instant-ngp/scripts/run.py", folder_path + "/" + folder_name + ".json", "--gui", "--train", "--n_step","5000", "--save_snapshot", "ingp/" + folder_name + ".ingp", "--save_mesh", "obj/" + folder_name + ".obj", "--marching_cubes_res", "400"])


if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    print("Script has started.")
    observer.schedule(event_handler, path="Z:\images\zip", recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
