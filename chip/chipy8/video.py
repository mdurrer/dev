#!/usr/bin/python
#* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#*   chipy8 - video.py                                                     *
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
import os
import sys
#import Numeric
import numpy
# for optimizing drawing:
from pygame import surfarray

class Video:
    def __init__(self, verbose = False, scale = 1):
        self.verbose = verbose
        self.scale = scale
        self.arraysize = (64,32)
        self.winsize = (self.arraysize[0] * self.scale, self.arraysize[1] * self.scale)
        self.__color_on = (0, 0, 0) # Black
        self.__color_off = (255, 240, 220) # White
        self.pixel_data = numpy.zeros( (64,32), 'i' )
        
        # Setup the pygame environment
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode(self.winsize, 0, 8)
        self.scale_screen = pygame.surface.Surface(self.arraysize, 0, 8)
        pygame.display.set_caption('chipy8')
        self.screen.fill(self.__color_off)
        self.scale_screen.fill(self.__color_off)

        self.screen.set_palette( [self.__color_off, self.__color_on] )
        self.scale_screen.set_palette( [self.__color_off, self.__color_on] )

    def draw8(self, ylines, regX, regY):
        collision = 0
        yline = 0
        for byte in ylines:
            byte = ylines[yline]
            for xline in range(8):
                if (byte & (0x80>>xline)) != 0:
                    x = (regX + xline) % 64
                    y = (regY + yline) % 32
                    if self.pixel_data[x][y] == 1:
                        self.pixel_data[x][y] = 0
                        collision = 1
                    else:
                        self.pixel_data[x][y] = 1
            yline = yline + 1

        surfarray.blit_array( self.scale_screen, self.pixel_data )
        temp = pygame.transform.scale(self.scale_screen, self.screen.get_size())
        self.screen.blit(temp, (0,0))
        pygame.display.update()
        return collision

    def erase(self):
        self.screen.fill(self.__color_off)
        pygame.display.flip()

