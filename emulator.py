import pygame
from chip8 import Chip8

pygame.init()
chip = Chip8()
screen = pygame.display.set_mode((chip.width * chip.scale_factor, chip.height * chip.scale_factor))
pygame.display.flip()
chip.skipto(0x200)
rlen = chip.load_rom("bc_test.ch8")
running = True
while running:
	#pygame.time.set_timer(pygame.USEREVENT + 1, round((1/60)*1000))
	chip.cycle()
	if chip.clear:
		screen.fill((0,0,0))
		pygame.display.flip()
		chip.pixels = []
		chip.clear = False
	else:
		for x, y in chip.pixels:
			pygame.draw.rect(screen, (255, 255, 255), 
				pygame.Rect(x * chip.scale_factor, 
					y * chip.scale_factor, 
					chip.scale_factor, 
					chip.scale_factor
				)
			)
		pygame.display.flip()
		chip.pixels = []
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
