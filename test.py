import pygame
from pygame.locals import *
pygame.init()
pygame.font.init()


def button(screen, color1, color2):
	mouse = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()
	print(mouse)
	if 352 > mouse[0] > 282 and 430 > mouse[1] > 400:
		pygame.draw.rect(screen, color2, (282, 400, 70,30))
		pygame.display.update()
		if click[0] == 1:
			pygame.quit()
	else:
		pygame.draw.rect(screen, color1, (282, 400, 70,30))
		pygame.display.update()

def main():
	(width, height) = ((1280,480))
	screen = pygame.display.set_mode((width, height))
	pygame.display.flip()
	background1 = pygame.image.load('M14_004.tif').convert()
	background1 = pygame.transform.scale(background1, (width//2, height))
	background2 = pygame.image.load('SkMel2_23.tif').convert()
	background2 = pygame.transform.scale(background2, (width//2, height))
	pygame.display.set_caption('Tutorial 1')
	screen.blit(background1, (0,0))
	screen.blit(background2, (width//2,0))
	pygame.display.flip()

	red = (200,0,0)
	bright_red = (255,0,0)

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
		button(screen, red,bright_red)
				
if __name__ == "__main__":
	main()