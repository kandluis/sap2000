from commandline import run
from time import strftime

outputfolder = 'C:\SAP 2000\\' +strftime("%b-%d") + "\\"
outputfilename = strftime("%H_%M_st%S")
program, model = run("",outputfolder + outputfilename)

from robots import Worker
from structure import Structure

structure = Structure()
worker = Worker("Bob",structure,(0,0,0))