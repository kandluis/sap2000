import sys
import subprocess

for chrom in range(1):
    theproc = subprocess.Popen([sys.executable, "run_test.py"])
    theproc.communicate()

