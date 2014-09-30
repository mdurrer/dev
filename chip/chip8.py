import os,sys,pygame
import machine
import cpu
from pygame.locals import *

def main():
	Frames = 60
	Running = True
	pygame.init()
	Clock = pygame.time.Clock()
	engine = machine.Machine()
	screen = pygame.display.set_mode((600,200),pygame.DOUBLEBUF|pygame.HWSURFACE,0)
	pygame.display.set_caption('Chip-8 Emulator')
	
	background = pygame.Surface (screen.get_size())
	background = background.convert()
	background.fill ((250,250,250))
	
	font = pygame.font.Font(None,36)
	text = font.render("Chip-8 Emulator", 1,(1,1,1))
	textpos = text.get_rect()
	textpos.centerx = background.get_rect().centerx
	background.blit(text,textpos)
	screen.blit(background,(0,0))
	pygame.display.flip()
	

	while Running:
		Clock.tick(60)
		for event in pygame.event.get():
			if event.type== pygame.QUIT:
				Running = False
				pygame.quit()
				return 1
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					Running = False
					pygame.quit()
			screen.blit(background,(0,0))
			pygame.display.flip()
	
if __name__ == '__main__': main()
