# X-ray emission & HERFD data analysis tool (Win / Linux / macOS)
X-ray emisson spectroscopy (XES) data analysis package

## Prerequisites
-	Python 3.5 or higher
-	Non-standard python package __PyQtGraph__ (http://www.pyqtgraph.org/), written by Luke Campagnola

It is recommended to use Anaconda (https://www.anaconda.com/) and run
```
conda install -c anaconda pyqtgraph
```

To enter the GUI, just type
```
python __main__.py 
```

## Features:
- Manage numerous scans and analyzer (ROIs) at the same time. View them separately, overlayed or summed (via linear interpolation) 
- Enable the automatic plotting-update to view and access changes quickly (e.g ROI size) 
