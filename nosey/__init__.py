import logging
from nosey.analyzer import Analyzer
from nosey.run import Run
from nosey.analysis import Analysis
from nosey.policy import ImportPolicy, DELTA_ImportPolicy, SOLEIL_ImportPolicy

__version__ = '0.1'                     #
lastComputationTime = 0.1
name = "nosey"

recipes = [DELTA_ImportPolicy, SOLEIL_ImportPolicy]   # Import modules

Log = logging.getLogger(__name__)
logging.basicConfig(level = logging.INFO)
