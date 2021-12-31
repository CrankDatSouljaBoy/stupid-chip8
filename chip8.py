import pygame
import random

class Chip8:
	def __init__(self):
		self.start_addr = 0x200
		self.fontset_start = 0x50
		self.memory = [0]*4096
		self.width = 64
		self.height = 32
		self.scale_factor = 16
		self.delay_timer = 0
		self.sound_timer = 0
		#self.frame_buffer = [0]*(self.width * self.height)
		self.clear = False
		self.pixels = []
		self.registers = [0]*(16)
		self.stack = [0]*(16)
		self.sp = 0
		self.stepPC = True
		self.pc = 0
		self.opcodes = {
			0x0000: self._0xxx,
			0x1000: self._1xxx,
			0x2000: self._2xxx,
			0x3000: self._3xxx,
			0x4000: self._4xxx,
			0x5000: self._5xxx,
			0x6000: self._6xxx,
			0x7000: self._7xxx,
			0x8000: self._8xxx,
			0x9000: self._9xxx,
			0xA000: self._Axxx,
			0xB000: self._Bxxx,
			0xC000: self._Cxxx,
			0xD000: self._Dxxx,
			0xE000: self._Exxx,
			0xF000: self._Fxxx,
    	}
		self._8xxx_opcodes = {
			0x0000: self._8xx0,
			0x0001: self._8xx1,
			0x0002: self._8xx2,
			0x0003: self._8xx3,
			0x0004: self._8xx4,
			0x0005: self._8xx5,
			0x0006: self._8xx6,
			0x0007: self._8xx7,
			0x000E: self._8xxE,
		}
		self.fontset = [	
			0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
			0x20, 0x60, 0x20, 0x20, 0x70, # 1
			0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
			0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
			0x90, 0x90, 0xF0, 0x10, 0x10, # 4
			0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
			0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
			0xF0, 0x10, 0x20, 0x40, 0x40, # 7
			0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
			0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
			0xF0, 0x90, 0xF0, 0x90, 0x90, # A
			0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
			0xF0, 0x80, 0x80, 0x80, 0xF0, # C
			0xE0, 0x90, 0x90, 0x90, 0xE0, # D
			0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
			0xF0, 0x80, 0xF0, 0x80, 0x80  # F 
		]
		for i, x in enumerate(self.fontset):
			self.memory[self.fontset_start + i] = x
		self.keymap = { 
			"1": 0x1, "2": 0x2, "3": 0x3, "4": 0xC,
			"Q": 0x4, "W": 0x5, "E": 0x6, "R": 0xD,
			"A": 0x7, "S": 0x8, "D": 0x9, "F": 0xE,
			"Z": 0xA, "X": 0x0, "C": 0xB, "V": 0xF,
			# French Key Mappings
			# "1": 0x1, "2": 0x2, "3": 0x3, "4": 0xC,
			# "A": 0x4, "Z": 0x5, "E": 0x6, "R": 0xD,
			# "Q": 0x7, "S": 0x8, "D": 0x9, "F": 0xE,
			# "Z": 0xA, "X": 0x0, "C": 0xB, "V": 0xF,
			# Standerd Mappings
			# "1": 0x1, "2": 0x2, "3": 0x3, "C": 0xC,
			# "4": 0x4, "5": 0x5, "6": 0x6, "D": 0xD,
			# "7": 0x7, "8": 0x8, "9": 0x9, "E": 0xE,
			# "A": 0xA, "0": 0x0, "B": 0xB, "F": 0xF,
		}

	def load_rom(self, filename):
		with open(filename, "rb") as f:
			byte = f.read()
			for i in range(len(byte)):
				self.memory[self.pc + i] = byte[i]

	def _0xxx(self, opcode):
		if opcode == 0x00E0:
			print("CLS")
			self.clear = True
		elif opcode == 0x00EE:
			print("RET")
			self.sp -= 1
			self.pc = self.stack[self.sp]

	def _1xxx(self, opcode):
		addr = opcode & 0x0FFF
		#print("JP ", hex(addr))
		self.pc = addr
		self.stepPC = False

	def _2xxx(self, opcode):
		addr = opcode & 0x0FFF
		print("CALL ", hex(addr))
		self.stack[self.sp] = self.pc
		print(self.stack[self.sp])
		self.sp += 1
		self.pc = addr

	def _3xxx(self, opcode):
		x = (opcode & 0x0F00) >> 8
		kk = opcode & 0x00FF
		print("SE ", hex(x), ", ", hex(kk))
		if self.registers[x] == kk:
			self.pc += 2

	def _4xxx(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		byte = opcode & 0x00FF
		print("SNE ", hex(Vx), ", ", hex(byte))
		if self.registers[Vx] != byte:
			self.pc += 2

	def _5xxx(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		Vy = (opcode & 0x00F0) >> 4
		print("SE ", hex(Vx), ", ", hex(Vy))
		if self.registers[Vx] == self.registers[Vy]:
			self.pc += 2

	def _6xxx(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		byte = opcode & 0x00FF
		print("SET ", hex(Vx), ", ", hex(byte))
		self.registers[Vx] = byte

	def _7xxx(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		byte = opcode & 0x00FF
		print("ADD ", hex(Vx), ", ", hex(byte))
		x = self.registers[Vx] + (opcode & 0x00FF)
		if x > 256: x = x - 256
		self.registers[Vx] = x

	def _8xx0(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		Vy = (opcode & 0x00F0) >> 4
		print("LD ", hex(Vx), ", ", hex(Vy))
		self.registers[Vx] += self.registers[Vy]
	
	def _8xx1(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		Vy = (opcode & 0x00F0) >> 4
		print("OR ", hex(Vx), ", ", hex(Vy))
		self.registers[Vx] |= self.registers[Vy]

	def _8xx2(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		Vy = (opcode & 0x00F0) >> 4
		print("AND ", hex(Vx), ", ", hex(Vy))
		self.registers[Vx] &= self.registers[Vy]
	
	def _8xx3(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		Vy = (opcode & 0x00F0) >> 4
		print("XOR ", hex(Vx), ", ", hex(Vy))
		self.registers[Vx] ^= self.registers[Vy]

	def _8xx4(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		Vy = (opcode & 0x00F0) >> 4
		print("ADD ", hex(Vx), ", ", hex(Vy))
		sum = self.registers[Vx] + self.registers[Vy]
		self.registers[0xF] = 0
		if sum > 255: 
			self.registers[0xF] = 1
		self.registers[Vx] = sum & 0xFF

	def _8xx5(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		Vy = (opcode & 0x00F0) >> 4
		print("SUB ", hex(Vy), ", ", hex(Vx))
		src = self.registers[Vy]
		tar = self.registers[Vx]
		if tar > src:
			tar -= src
			self.registers[0xF] = 1
		else:
			tar = 256 + tar - src
			self.registers[0xF] = 0
		self.registers[Vx] = tar
	
	def _8xx6(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		Vy = (opcode & 0x00F0) >> 4
		print("SHR ", hex(Vx), ", ", hex(Vy))
		self.registers[0xF] = self.registers[Vx] & 0x01
		print(self.registers[0xF])
		self.registers[Vx] >>= 1
	
	def _8xx7(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		Vy = (opcode & 0x00F0) >> 4
		print("SUBN ", hex(Vx), ", ", hex(Vy))
		self.registers[0xF] = 0
		if self.registers[Vy] > self.registers[Vx]:
			self.registers[0xF] = 1
		self.registers[Vx] = self.registers[Vy] - self.registers[Vx]

	def _8xxE(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		Vy = (opcode & 0x00F0) >> 4
		print("SHL ", hex(Vx), ", ", hex(Vy))
		# okay what the hell
		self.registers[0xF] = self.registers[Vx] >> 7
		print(self.registers[0xF])
		self.registers[Vx] = (self.registers[Vx] << 1) & 0xFF

	def _8xxx(self, opcode):
		Bw = opcode & 0x000F
		self._8xxx_opcodes.get(Bw)(opcode)

	def _9xxx(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		Vy = (opcode & 0x00F0) >> 4
		if self.registers[Vx] != self.registers[Vy]:
			self.pc += 2

	def _Axxx(self, opcode):
		addr = opcode & 0x0FFF
		print("LD I, ", hex(addr))
		self.index = addr

	def _Bxxx(self, opcode):
		addr = opcode & 0x0FFF
		print("JP V0, ", hex(addr))
		self.pc = self.registers[0] + addr

	def _Cxxx(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		byte = opcode & 0x00FF
		print("RND ", hex(Vx), ", ", hex(byte))
		self.registers[Vx] = random.randint(0, 255) & byte

	def _Dxxx(self, opcode):
		Vx = (opcode & 0x0F00) >> 8
		Vy = (opcode & 0x00F0) >> 4
		height = opcode & 0x000F
		print("DRW ", hex(Vx), ", ", hex(Vy), ", ", hex(height))
		x = self.registers[Vx] % self.width
		y = self.registers[Vy] % self.height
		self.registers[0xF] = 0
		for row in range(0, height):
			sprite = self.memory[self.index + row]
			for col in range(0, 8):
				sprite_pixel = sprite & (0x80 >> col)
				#screen_pixel = self.frame_buffer[(y + row) * self.width + (x + col)]
				if sprite_pixel:
					#if screen_pixel == 0xFFFFFFFF:
					#	self.registers[0x1F] = 1
					self.pixels.append(((x + col), (y + row)))

	def _Exxx(self, opcode):
		#keyboard
		Bw = opcode & 0x00FF
		Vx = (opcode & 0x0F00) >> 8
		if Bw == 0x009E:
			print("SKP ", Vx)
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.KEYDOWN:
					key = pygame.key.name(event.key).upper()
					if key in self.keymap.keys():
						if self.keymap[key] == Vx:
							self.pc += 2
		elif Bw == 0x00A1:
			print("SKNP ", Vx)
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.KEYDOWN:
					key = pygame.key.name(event.key).upper()
					if key not in self.keymap.keys():
						self.pc += 2
					else:
						if self.keymap[key] is not Vx:
							self.pc += 2

	def _Fxxx(self, opcode):
		Bw = opcode & 0x00FF
		Vx = (opcode & 0x0F00) >> 8
		if Bw == 0x0007:
			print("LD ", Vx, ", DT")
			self.registers[Vx] = self.delay_timer
		if Bw == 0x000A:
			# wait for keypress
			print("LD ", Vx, ", K")
			print("waiting for keypress...")
			event = pygame.event.wait()
			if event.type == pygame.KEYDOWN:
				key = pygame.key.name(event.key).upper()
				if key in self.keymap.keys():
					self.registers[Vx] = self.keymap[key]
				else:
					self.pc -= 2
			else:
				self.pc -= 2
		if Bw == 0x0015:
			print("LD DT, ", Vx)
			self.delay_timer = self.registers[Vx]
		if Bw == 0x0018:
			print("LD ST, ", Vx)
			self.sound_timer = self.registers[Vx]
		if Bw == 0x001E:
			print("ADD I, ", Vx)
			self.index += self.registers[Vx]
		if Bw == 0x0029:
			print("LD F, ", Vx)
			self.index = self.fontset_start + (5 * self.registers[Vx])
		if Bw == 0x0033:
			print("LD B, ", Vx)
			bcd_value = '{:03d}'.format(self.registers[Vx])
			self.memory[self.index] = int(bcd_value[0])
			self.memory[self.index + 1] = int(bcd_value[1])
			self.memory[self.index + 2] = int(bcd_value[2])
		if Bw == 0x0055:
			print("LD [I], ", Vx)
			for counter in range(Vx + 1):
				self.memory[self.index + counter] = self.registers[counter]
		if Bw == 0x0065:
			print("LD ", Vx, ", [I]")
			Vx = (opcode & 0x0F00) >> 8
			for counter in range(Vx + 1):
				self.registers[counter] = self.memory[self.index + counter]

	def skipto(self, addr):
		self.pc = addr

	def cycle(self):
		opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
		mask = opcode & 0xF000
		self.pc += 2
		self.opcodes.get(mask)(opcode)
		if self.delay_timer > 0: self.delay_timer -= 1
		if self.sound_timer > 0: self.sound_timer -= 1
