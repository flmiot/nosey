# Design   
ffi aims at beeing a beamline tool for fast explorative data analysis.
It's main goal is to get meaningful feedback about aquired data as fast as
possible.

## The basic principles are:

1.   Ease of use: Minimal dependencies, pure python, documentation, examples:
    -   No extensive knowledge of python should be required for use
    -   Both beginners and experienced users should be able to benefit
2.   Work with the raw image files alone as long as possible (ease of use)
    -   Easier to setup because only reduced adaptions to the beamline necessary
    -   More meta-data can be added/imported on an as-needed basis
    -   More meta-data should be optional and scans should be resolved smartly
4.   Modularity: code base detached from everything GUI, modular code base
    -   Strict separation between "functional core" and GUI (works without GUI!)
5.   Should come with a complete and mature GUI, which exposes all functions
    -   Reliable GUI which follows the needs during exploratory data analysis
6.   Flexibility: adaptable to both synchrotron and FEL beamlines
    -   Native treatment of transient scans and pump-probe experiments
7.   Completeness: Offer set of standard tools to help navigate the experiment:
    -   Background subtraction
    -   Integrated absolute difference
    -   Center-of-mass shift of curves
    -   Normalisation to Area / Peak-height
    -   Differences / transients
    -   HERFD scanning mode
    -   Full error propagation
    -   Curve fitting

integration
detector
explorative
data
analysis
synchrotron
2d
multi-dimension
rapid
X-ray
Emission
Spectroscopy
Scattering
Inelastic
Tool
live
fel
sum
dispersive
fast
feedback

von Hamos
