# Design   
NOSEY aims at beeing a beamline tool for fast explorative data analysis

## The basic design principles are:
    -   Ease of use: Minimal dependencies, pure python, documentation, examples
    -   Work with the raw image files alone as long as possible (ease of use)
    -   More meta-data can be added/imported on an as-needed basis
    -   Modularity: code base detached from everything GUI, modular code base
    -   Should come with a complete and mature GUI, which exposes all functions
    -   Flexibility: adaptable to both synchrotron and FEL beamlines
    -   Complete set of standard tools to help navigate the experiment:
        -   Background subtraction
        -   Integrated absolute difference
        -   Center-of-mass shift of curves
        -   Normalisation to Area / Peak-height
        -   Differences / transients
        -   HERFD scanning mode
        -   Full error propagation
        -   Curve fitting
