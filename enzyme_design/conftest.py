"""Make the ``enzyme_design`` package importable no matter where pytest is run."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
