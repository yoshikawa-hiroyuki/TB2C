import threading
import time

import TSData
e = threading.Event()

def Loader(d):
    d.loadCheck(['p_001.sph', 'p_002.sph', 'p_003.sph'],
                '/Users/yoh/Works/Vtools/data/obstacle')
    e.set()

d = TSData.TSDataSph()
t = threading.Thread(target=Loader, args=([d]))
t.setDaemon(True)
t.start()

for i in range(10):
    time.sleep(0.3)
    print(d._curIdx)
    if e.is_set(): break
    
print('done.')
