#!/usr/bin/python
#* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#*   chipy8 - chipy8.py                                                    *
#*   chipy8 homepage: http://code.google.com/p/chipy8/                     *
#*   Copyright (C) 2009 olejl77@gmail.com                                  *
#*                                                                         *
#*   This program is free software: you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation, either version 3 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          *
#*   GNU General Public License for more details.                          *
#*                                                                         *
#*   You should have received a copy of the GNU General Public License     *
#*   along with this program.  If not, see <http://www.gnu.org/licenses/>. *
#* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
import sys
import os
from optparse import OptionParser
from cpu import Cpu

# Options, usage and stuff...
ver = "%prog - version 0.1"
usage = "usage: '%prog [options] GAME'\n\n"
usage += "chipy8 is a Chip8 emulator written in Python using pygame.\n"
parser = OptionParser(usage, version=ver)
parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Print debug information')
parser.add_option('-i', '--ips', action='store', dest='ips', type='float', default=60, help='How many instructions to execute each second')
parser.add_option('-s', '--scale', action='store', dest='scale', type='int', default=1, help='Increase the window size with the scale factor')
(options, args) = parser.parse_args()
if len(args) != 1:
    parser.error("Wrong number of arguments specified")
else:
    if not os.path.exists(args[0]):
        parser.error("File doesn't exist")
    else:
        if os.path.getsize(args[0]) > 0x0fff:
            parser.error("File to large")
    
cpu = Cpu(options.verbose, options.scale)
cpu.read_rom(args[0])
cpu.run(options.ips)

