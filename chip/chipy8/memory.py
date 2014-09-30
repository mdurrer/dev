#!/usr/bin/python
#* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#*   chipy8 - memory.py                                                    *
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
import pygame
import array
import struct

class Memory:
    def __init__(self):
        # Memory
        self._memory = array.array('B') # creating an array of unsigned chars

        # Inserting the font data. Starting in memory position 0
        # 0
        self._memory.append(0b11110000)
        self._memory.append(0b10010000)
        self._memory.append(0b10010000)
        self._memory.append(0b10010000)
        self._memory.append(0b11110000)
        # 1
        self._memory.append(0x20) #0010 0000
        self._memory.append(0x60) #0110 0000
        self._memory.append(0x20) #0010 0000
        self._memory.append(0x20) #0010 0000
        self._memory.append(0x70) #0111 0000
        # 2
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x10) #0001 0000
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x80) #1000 0000
        self._memory.append(0xf0) #1111 0000
        # 3
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x10) #0001 0000
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x10) #0001 0000
        self._memory.append(0xf0) #1111 0000
        # 4
        self._memory.append(0x90) #1001 0000
        self._memory.append(0x90) #1001 0000
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x10) #0001 0000
        self._memory.append(0x10) #0001 0000
        # 5
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x80) #1000 0000
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x10) #0001 0000
        self._memory.append(0xf0) #1111 0000
        # 6
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x80) #1000 0000
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x90) #1001 0000
        self._memory.append(0xf0) #1111 0000
        # 7
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x10) #0001 0000
        self._memory.append(0x20) #0010 0000
        self._memory.append(0x40) #0100 0000
        self._memory.append(0x40) #0100 0000
        # 8
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x90) #1001 0000
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x90) #1001 0000
        self._memory.append(0xf0) #1111 0000
        # 9
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x90) #1001 0000
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x10) #0001 0000
        self._memory.append(0xf0) #1111 0000
        # A
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x90) #1001 0000
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x90) #1001 0000
        self._memory.append(0x90) #1001 0000
        # B
        self._memory.append(0xe0) #1110 0000
        self._memory.append(0x90) #1001 0000
        self._memory.append(0xe0) #1110 0000
        self._memory.append(0x90) #1001 0000
        self._memory.append(0xe0) #1110 0000
        # C
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x80) #1000 0000
        self._memory.append(0x80) #1000 0000
        self._memory.append(0x80) #1000 0000
        self._memory.append(0xf0) #1111 0000
        # D
        self._memory.append(0xe0) #1110 0000
        self._memory.append(0x90) #1001 0000
        self._memory.append(0x90) #1001 0000
        self._memory.append(0x90) #1001 0000
        self._memory.append(0xe0) #1110 0000
        # E
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x80) #1000 0000
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x80) #1000 0000
        self._memory.append(0xf0) #1111 0000
        # F
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x80) #1000 0000
        self._memory.append(0xf0) #1111 0000
        self._memory.append(0x80) #1000 0000
        self._memory.append(0x80) #1000 0000

        # pad the memory up to 0x200 where the ROM will start
        for i in range(0x200 - len(self._memory)):
            self._memory.append(0)    # with 0.
            
    def read(self, address):
        return self._memory[address]
    
    def write(self, address, value):
        self._memory[address] = value
        
    def read_rom(self, filename):
        with open(filename, "rb") as f:
            byte = f.read(1)
            while byte:
                self._memory.append(struct.unpack('B', byte)[0])
                byte = f.read(1)
        # After the ROM is loaded, make sure that the complete memory is initialized
        while (len(self._memory) < 0x1000):
            self._memory.append(0)

