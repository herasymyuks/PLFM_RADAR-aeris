"""Signal processing: CA-CFAR, DBSCAN clustering, Kalman tracking.

Provenance: ``clustering`` and ``tracking`` are lifted from
``GUI_V5.RadarProcessor`` (``GUI_V5.py:587-670``), which defined them but
never called them.  No GUI version contained a CFAR implementation (the FPGA
flag was expected instead); ``cfar`` is new.
"""
from .cfar import ca_cfar_1d, ca_cfar_2d, cfar_detections, cfar_scale_factor  # noqa: F401
from .clustering import Cluster, cluster_points  # noqa: F401
from .tracking import Track, Tracker  # noqa: F401
