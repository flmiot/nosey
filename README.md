# X-ray emission data analysis tool (Win / Linux / macOS)

![alt text](https://github.com/flmiot/nosey/blob/stable/doc/overview.png)

## Prerequisites
-	Python 3.5 or higher
-	Non-standard python package __PyQtGraph__ (http://www.pyqtgraph.org/), written by Luke Campagnola

It is recommended to use Anaconda (https://www.anaconda.com/) and run
```
conda install -c anaconda pyqtgraph
```

To enter the GUI, just type
```
python __main__.py [input_file.dat]
```

## Save & load analysis projects
Input files can be specified in the command line or selected via the GUI. The
current project can be saved at any time via GUI by clicking the save icon.

Recognized **plotting keywords** are
- ```!PLOT```   
 Plot the energy spectrum after input file processing was finished

- ```!NORMALIZE```  
 Normalize the area under the curve for the energy spectrum to 1000

- ```!SINGLE_SCANS```  
 Plot each scan separately, allowing for visual inspection of differences

- ```!SINGLE_ANALYZERS```  
 Plot each analyzer signal separately, allowing for visual inspection of differences

- ```!SUBTRACT_MODEL```  
 Subtract the background, if there is one

- ```!AUTO```   
 Plot the energy spectrum automatically everytime something changes

Recognized **analysis keywords** are
- ```!SCANS```
- ```!ANALYZERS```
- ```!CALIBRATIONS```
- ```!GROUPS```
- ```!REFERENCES```
- ```!SETTINGS```


Specifiy
**scans** as
```
!SCANS
scan(path, include, group)
scan(...)
...
```
**analyzers** as

```
!ANALYZERS
analyzer(include, position-x, position-y, width, height, bg01-distance,
  bg02-distance, bg01-height, bg02-height, energy-points)
analyzer(...)
...
```

**calibrations** as

```
!CALIBRATIONS
energy(position)
energy(...)
...
```

**groups** as

```
!GROUPS
group(include, reference, name)
group(...)
...
```

**reference** as

```
!REFERENCES
reference(path, r1, r2, name)
reference(...)
...
```

A number of example input files can be found under /examples.

## Features:
- Manage numerous scans and analyzer (ROIs) at the same time. View them separately, overlayed or summed (via linear interpolation)
- Enable the automatic plotting-update to view and access changes quickly (e.g ROI size)
