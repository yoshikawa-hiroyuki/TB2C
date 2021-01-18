# TB2C -<i>Temporal Buffer to ChOWDER prototype</i>

## Requires
### Node.js

### obj23dtiles
```
sudo npm install -g obj23dtiles
```

### Python3.x

### NumPy
```
sudo pip3 install numpy
```

### wxPython
```
sudo pip3 install wxPython
```

### PyOpenGL
```
sudo pip3 install PyOpenGL
```

### websocket-client
```
sudo pip3 install websocket-client
```

--------
## Run TB
```
python3 python/TB.py [-j sphlist.json | -l sphfile ...]
```

## Run TB2C server
```
python3 python/TB2C_server.py [--port portNo] ¥
    [--odir outDir] [--dx divX] [--dy divY] [--dz divZ]
```

## Run TB2C server
```
python3 python/TB2C_client.py [-s http://localhost:4000/] [-c localhost]
```
