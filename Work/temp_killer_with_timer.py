import os, time, sys, sched

s = sched.scheduler(time.time, time.sleep)
def run_killer(sc):
    paths = [r'C:\Users\geo_flpo\.snap\var\cache\temp', r'C:\Users\geo_flpo\AppData\Local\Temp\8']
    now = time.time()
    print(now)
    for i, path in enumerate(paths):
        files_before = len(os.listdir(path))
        for f in os.listdir(path):
            if i == 0:
                if os.stat(os.path.join(path,f)).st_mtime < now - 120*60:
                    try:
                        os.remove(os.path.join(path, f))
                    except WindowsError as e:
                        #print(e.winerror)
                        continue
            else:
                if os.stat(os.path.join(path,f)).st_mtime < now - 30*60:
                    try:
                        os.remove(os.path.join(path, f))
                    except WindowsError as e:
                        #print(e.winerror)
                        continue
        print(str(files_before - len(os.listdir(path))) + ' files deleted')

    s.enter(30*60, 1, run_killer, (sc,))





s.enter(30*60, 1, run_killer, (s,))
s.run()

