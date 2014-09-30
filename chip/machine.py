import os,sys,pygame
import cpu

class Machine:
	""" Main class for the Emulation Engine / Machine """
	def __init__(self):
		self.Name = "Chip-8 Emulator"
		self.Version = 0.1
		print ("Initializing " + self.Name + " ", self.Version )
		self.CPU = cpu.CPU()
		
