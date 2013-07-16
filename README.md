Decentralized Collective Construction
=============

INSTALLATION STEPS

Download and Install:
	SAP2000 v15
  Python 3.2.x
  PyWin32 Module
  VPython for Python 3.2

Simulation Suite for the construction of tower. Construction based only on local
data derived by SAP2000 program.

Directory Structure
=======
* swarm/                          Top-level swarm package
        * __init__.py              
        * helpers/                  Subpackage containing * helper files
                * __init__.py
                * commandline.py
                * errors.py
                * helpers.py
                * inout.py
                * vectors.py
        * robots/                  Subpackage for robot swarm
                * __init__.py
                * automaton.py
                * builder.py
                * colony.py
                * movable.py
                * worker.py
        * sap2000/                  Subpackage for  communication
                * __init__.py
                * constants.py
                * sap2000.py
                * sap_analysis.py
                * sap_areas.py
                * sap_base.py
                * sap_frames.py
                * sap_groups.py
                * sap_lines.py
                * sap_points.py
                * sap_properties.py
        * structure/                  Subpackage for python structure
                * __init__.py
                * beams.py
                * structure.py
        * construction.py   Constants for construction (limits,etc)
        * main.py   
        * run_test.py   
        * variables.py    Constants for the program
        * vis_test.py   
        * visualization.py  
