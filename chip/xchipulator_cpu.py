from random import randint

class Chip8CPU:
    def __init__(self, gamepad, canvas, filename):
        """Initialize a chip8 CPU by passing in its gamepad, canvas and a ROM
        filename.
        
        """
        self._gamepad = gamepad
        self._canvas = canvas
        
        # Initialize memory with font data and pad to ROM accessible area.
        self._initMemory()
        # Load the ROM data into memory
        self._loadROM(filename)
        # Pad to the end of memory
        self._padMemory(0xFFF)
        
        # Initialize registers, stack pointer etc
        self._resetSystem()
        
        # Opcode to method name map
        self._optable_main = {
            0x0: self._op_0_nest,
            0x1: self._op_jmp,
            0x2: self._op_jsr,
            0x3: self._op_skeq,
            0x4: self._op_skne,
            0x5: self._op_sker,
            0x6: self._op_mov,
            0x7: self._op_add,
            0x8: self._op_8_nest,
            0x9: self._op_skner,
            0xA: self._op_mvi,
            0xB: self._op_jmi,
            0xC: self._op_rand,
            0xD: self._op_sprite,
            0xE: self._op_E_nest,
            0xF: self._op_F_nest
        }
        
        self._optable_0_E = {
            0xE0: self._op_cls,
            0xEE: self._op_rts
        }
        
        self._optable_0_F = {
            0xFB: self._op_scr,
            0xFC: self._op_scl,
            0xFD: self._op_end,
            0xFE: self._op_dex,
            0xFF: self._op_eex
        }
        
        self._optable_8 = {
            0x0: self._op_movr,
            0x1: self._op_or,
            0x2: self._op_and,
            0x3: self._op_xor,
            0x4: self._op_addr,
            0x5: self._op_sub,
            0x6: self._op_shr,
            0x7: self._op_rsb,
            0xE: self._op_shl
        }
        
        self._optable_E = {
            0xE: self._op_skpr,
            0x1: self._op_skup
        }
        
        self._optable_F = {
            0x07: self._op_gdelay,
            0x0A: self._op_key,
            0x15: self._op_sdelay,
            0x18: self._op_ssound,
            0x1E: self._op_adi,
            0x29: self._op_nfnt, 
            0x30: self._op_efnt,           
            0x33: self._op_bcd,
            0x55: self._op_str,
            0x65: self._op_ldr,
            0x75: self._op_shpf,
            0x85: self._op_lhpf,
        }
        
    def nextCycle(self):
        """Reads and executes the next instruction."""
        instruction = (self._memory[self._PC] << 8) + self._memory[self._PC + 1]
        self._executeInstruction(instruction)
    
    def getSoundTimer(self):
        """Returns the Chip-8 sound timer."""
        return self._soundTimer
    
    def getDelayTimer(self):
        """Returns the Chip-8 delay timer."""
        return self._delayTimer
    
    def getVRAM(self):
        """Return the VRAM"""
        return self._VRAM
    
    def isHalted(self):
        """Boolean getter for the CPU halt status (CPU will pause if waiting
        for a keypad input).
        
        """
        return self._halted
    
    def decrementSoundTimer(self):
        """Decrements the sound timer."""
        self._soundTimer -= 1
    
    def decrementDelayTimer(self):
        """Decrements the delay timer."""
        self._delayTimer -= 1
    
    def coreDump(self):
        """Return the CPU program counter, stack, stack pointer, registers,
        address register, delay timer, sound timer, halt status, keypad status,
        video mode, video memory, lower bound of any modified memory
        and the modified memory itself.
        
        """
        tempDump = []
        
        # Append simple data
        tempDump.append(self._PC)
        tempDump.append(self._stack)
        tempDump.append(self._stackPointer)
        tempDump.append(self._register)
        tempDump.append(self._addressRegister)
        
        tempDump.append(self._delayTimer)
        tempDump.append(self._soundTimer)
        tempDump.append(self._halted)
        tempDump.append(self._gamepad.getKeyTable())
        tempDump.append(self._displayMode)
        
        tempDump.append(self._VRAM)
        
        # Calculate the lower and upper bounds for modified program memory
        # (if any)
        memUpperBound = 0x200
        memLowerBound = 0x200
        
        for i in xrange(0xFFF, 0x200, -1):
            if(self._memory[i - 1] != 0x00):
                memUpperBound = i
                break
        
        for i in xrange(0x200, min(memUpperBound, len(self._ROM) + 0x200)):
            if(self._memory[i] != self._ROM[i - 0x200]):
                memLowerBound = i
                break
        
        modifiedProgramMemory = self._memory[memLowerBound : memUpperBound]
        
        tempDump.append(memLowerBound)
        tempDump.append(modifiedProgramMemory)
        
        return tempDump
    
    def unCoreDump(self, memoryDump):
        """Accepts a memory dump list and loads it into the CPU."""
        
        self._PC, \
        self._stack, \
        self._stackPointer, \
        self._register, \
        self._addressRegister, \
        self._delayTimer, \
        self._soundTimer, \
        self._halted, \
        keyTable, \
        displayMode, \
        VRAM, \
        memLowerBound, \
        modifiedProgramMemory = memoryDump
        
        # Load in the keyTable
        self._gamepad.setKeyTable(keyTable)
        # Load in the VRAM after initializing display
        self._setDisplayMode(displayMode)
        self._VRAM = VRAM
        # Initialize and load in the program memory
        self._initMemory()
        self._loadROM(limit=(memLowerBound - 0x200))
        self._memory.extend(modifiedProgramMemory)
        self._padMemory(0xFFF)
    
    def reset(self):
        """Reset the CPU"""
        self._initMemory()
        self._loadROM()
        self._padMemory(0xFFF)
        self._setDisplayMode(0)
        self._resetSystem()
    
    def _setDisplayMode(self, mode):
        """Configure the internal VRAM and canvas to extended / standard
        mode.
        
        """
        if(mode == 1):
            # Extended mode
            self._initVRAM([128, 64])
            self._canvas.setDisplayProperties(128, 64)
            self._displayMode = 1
        elif(mode == 0):
            # Standard mode
            self._initVRAM([64, 32])
            self._canvas.setDisplayProperties(64, 32)
            self._displayMode = 0
    
    def _executeInstruction(self, instruction):
        """Execute an instruction."""
        # Store some common bit masks
        self._X = (instruction & 0x0F00) >> 8
        self._Y = (instruction & 0x00F0) >> 4
        self._N  = instruction & 0x000F
        self._NN  = instruction & 0x00FF
        self._NNN = instruction & 0x0FFF
        # Send the instruction to the opcode table
        self._optable_main[instruction >> 12]()
    
    def _initMemory(self):
        """Initialize the system memory with font data and pad to 0x200."""
        # Load the font data into memory[0x00 : 0xF0]
        self._memory = [
            # 8x5 font data
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x60, 0x20, 0x20, 0x20, 0xF0,
            0xF0, 0x10, 0xF0, 0x80, 0xF0,
            0xF0, 0x10, 0xF0, 0x10, 0xF0,
            0x90, 0x90, 0xF0, 0x10, 0x10,
            0xF0, 0x80, 0xF0, 0x10, 0xF0,
            0xF0, 0x80, 0xF0, 0x90, 0xF0,
            0xF0, 0x10, 0x10, 0x10, 0x10,
            0xF0, 0x90, 0xF0, 0x90, 0xF0,
            0xF0, 0x90, 0xF0, 0x10, 0x10,
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xC0, 0xA0, 0xC0, 0xA0, 0xC0,
            0xF0, 0x80, 0x80, 0x80, 0xF0,
            0xC0, 0xA0, 0xA0, 0xA0, 0xC0,
            0xF0, 0x80, 0xF0, 0x80, 0xF0,
            0xF0, 0x80, 0xC0, 0x80, 0x80,
            
            # 16x10 font data (taken from David Winter's documentation)
            0xF0, 0xF0, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0xF0, 0xF0, # 0
            0x20, 0x20, 0x60, 0x60, 0x20, 0x20, 0x20, 0x20, 0x70, 0x70,
            0xF0, 0xF0, 0x10, 0x10, 0xF0, 0xF0, 0x80, 0x80, 0xF0, 0xF0,
            0xF0, 0xF0, 0x10, 0x10, 0xF0, 0xF0, 0x10, 0x10, 0xF0, 0xF0,
            0x90, 0x90, 0x90, 0x90, 0xF0, 0xF0, 0x10, 0x10, 0x10, 0x10,
            0xF0, 0xF0, 0x80, 0x80, 0xF0, 0xF0, 0x10, 0x10, 0xF0, 0xF0,
            0xF0, 0xF0, 0x80, 0x80, 0xF0, 0xF0, 0x90, 0x90, 0xF0, 0xF0,
            0xF0, 0xF0, 0x10, 0x10, 0x20, 0x20, 0x40, 0x40, 0x40, 0x40,
            0xF0, 0xF0, 0x90, 0x90, 0xF0, 0xF0, 0x90, 0x90, 0xF0, 0xF0,
            0xF0, 0xF0, 0x90, 0x90, 0xF0, 0xF0, 0x10, 0x10, 0xF0, 0xF0,
            0xF0, 0xF0, 0x90, 0x90, 0xF0, 0xF0, 0x90, 0x90, 0x90, 0x90, # A
            0xE0, 0xE0, 0x90, 0x90, 0xE0, 0xE0, 0x90, 0x90, 0xE0, 0xE0,
            0xF0, 0xF0, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0xF0, 0xF0,
            0xE0, 0xE0, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0xE0, 0xE0,
            0xF0, 0xF0, 0x80, 0x80, 0xF0, 0xF0, 0x80, 0x80, 0xF0, 0xF0,
            0xF0, 0xF0, 0x80, 0x80, 0xF0, 0xF0, 0x80, 0x80, 0x80, 0x80,
        ]
        
        # Pad up to program memory
        self._padMemory(0x200)
    
    def _padMemory(self, endOffset):
        """Pad the program memory with zeros to the specified offset."""
        self._memory.extend([0x0] * (endOffset - len(self._memory)))
    
    def _resetSystem(self):
        """Reset timers, registers and bit masks"""
        # Timers
        self._delayTimer = 0x00
        self._soundTimer = 0x00
        self._halted = 0
        
        # Initialize registers etc
        self._PC = 0x200
        self._addressRegister = 0x0000     
        self._register = [0x00] * 16     
        self._stack = [0x0000] * 16
        self._stackPointer = 0x0
        self._hp48Flags = [0x00] * 8
        self._setDisplayMode(0)
        
        # Common bit masks for instructions
        self._X = 0x0
        self._Y = 0x0
        self._N = 0x0
        self._NN = 0x00
        self._NNN = 0x000
    
    def _loadROM(self, fileName=None, limit=None):
        """Load a ROM file into program memory."""
        if(fileName is not None):
            fh = open(fileName, 'rb')
            romString = fh.read()
            fh.close()
            # Explode the string, then convert each element to a hex value
            self._ROM = map(ord, list(romString))
        
        # Only a portion of the ROM may need to be loaded if a core dump file
        # being loaded into the CPU.
        if(limit is not None):
            self._memory.extend(self._ROM[ : limit])
        else:
            self._memory.extend(self._ROM)
    
    def _stackPop(self):
        """Pop the stack."""
        self._stackPointer -= 1
        return self._stack[self._stackPointer]
    
    def _stackPush(self, int):
        """Push an integer onto the stack."""
        self._stack[self._stackPointer] = int
        self._stackPointer += 1
    
    def _initVRAM(self, dimensions):
        """Store the VRAM dimensions and clear the VRAM."""
        self._VRAMX, self._VRAMY = dimensions
        self._clearVRAM()
    
    def _clearVRAM(self):
        """Fill the VRAM with zeros."""
        self._VRAM = []
        self._VRAM = [[0x0] * self._VRAMX for i in xrange(self._VRAMY)]
    
    def _op_0_nest(self):
        """Nested opcode map for opcodes in the 0x0 range"""
        # Slighly more complex since most SCHIP opcodes are implemented here
        if(self._Y == 0xC):
            self._op_scd()
        elif(self._Y == 0xE):
            self._optable_0_E[self._NN]()
        elif(self._Y == 0xF):
            self._optable_0_F[self._NN]()
    
    def _op_8_nest(self):
        """Nested opcode map for opcodes in the 0x8 range"""
        self._optable_8[self._N]()
    
    def _op_E_nest(self):
        """Nested opcode map for opcodes in the 0xE range"""
        self._optable_E[self._N]()
    
    def _op_F_nest(self):
        """Nested opcode map for opcodes in the 0xF range"""
        self._optable_F[self._NN]()
    
    def _op_scd(self):
        """OPCODE SCHIP scd (0x00CN): Scroll the screen down N lines"""
        oldVRAM = self._VRAM
        self._clearVRAM()   
        self._VRAM[self._N : ] = oldVRAM[ : -self._N]
        self._PC += 2
    
    def _op_scr(self):
        """OPCODE SCHIP scr (0x00FB): Scroll the screen right 4/2 pixels"""
        if(self._displayMode == 1):
            pixelCount = 4
        else:
            pixelCount = 2
            
        for y in xrange(self._VRAMY):
            newVRAM = [0x0] * pixelCount
            newVRAM.extend(self._VRAM[y][ : -pixelCount])
            self._VRAM[y] = newVRAM
        self._PC += 2
    
    def _op_scl(self):
        """OPCODE SCHIP scl (0x00FC): Scroll the screen left 4/2 pixels"""
        if(self._displayMode == 1):
            pixelCount = 4
        else:
            pixelCount = 2
            
        for y in xrange(self._VRAMY):
            newVRAM = self._VRAM[y][pixelCount : self._VRAMX]
            newVRAM.extend([0x0] * pixelCount)
            self._VRAM[y] = newVRAM
        self._PC += 2
    
    def _op_end(self):
        """OPCODE SCHIP end (0x00FD): End emulation"""
        self._halted = 1
    
    def _op_eex(self):
        """OPCODE SCHIP eex (0x00FF): Enable extended screen mode"""
        self._setDisplayMode(1)     
        self._PC += 2
    def _op_dex(self):
        """OPCODE SCHIP dex (0x00FE): Disable extended screen mode"""
        self._setDisplayMode(0)        
        self._PC += 2
    
    def _op_efnt(self):
        """OPCODE SCHIP efnt (0xFX29): Set the address register to the location
        of extended font data for character in register[X]
        
        """
        # Extended fonts are stored at 0x000 onward and take up 10 bytes each        
        self._addressRegister = 0x50 + self._register[self._X] * 10
        self._PC += 2
    
    def _op_shpf(self):
        """OPCODE SCHIP shpf(0xFX75): Store register[0 : X] in HP48 flags. X < 8
        
        """
        for i in xrange(self._X + 1):
            self._hp48Flags[i] = self._register[i]
        self._PC += 2
    
    def _op_lhpf(self):
        """OPCODE SCHIP lhpf(0xFX85): Load register[0 : X] from HP48 flags. X < 8
        
        """
        for i in xrange(self._X + 1):
            self._register[i] = self._hp48Flags[i]
        self._PC += 2
    
    def _op_cls(self):
        """OPCODE cls (0x00E0): Clear the VRAM"""
        self._clearVRAM()
        self._PC += 2        
    
    def _op_rts(self):
        """OPCODE rts (0x00EE): Return from subroutine, I.E pop the register
        and update the program counter
        
        """
        self._PC = self._stackPop() + 2
    
    def _op_jmp(self):
        """OPCODE jmp (0x1NNN): Set the PC to NNN"""
        if(self._NNN == self._PC):
            self._op_end()
        else:
            self._PC = self._NNN
    
    def _op_jsr(self):
        """OPCODE jsr (0x2NNN): Jump to subroutine at address NNN
        
        """
        self._stackPush(self._PC)
        self._PC = self._NNN
    
    def _op_skeq(self):
        """OPCODE skeq (0x3XNN): Skip next instruction if register[X] == NN"""
        if(self._register[self._X] == self._NN):
            self._PC += 4
        else:
            self._PC += 2
    
    def _op_skne(self):
        """OPCODE skne (0x4XNN): Skip next instruction if register[X] != NN"""
        if(self._register[self._X] != self._NN):
            self._PC += 4
        else:
            self._PC += 2
    
    def _op_sker(self):
        """OPCODE sker (0x5XY0): Skip next instruction
        if register[X] == register[Y]
        
        """
        if(self._register[self._X] == self._register[self._Y]):
            self._PC += 4
        else:
            self._PC += 2
    
    def _op_mov(self):
        """OPCODE mov (0x6XNN): Set register[X] to NN"""
        self._register[self._X] = self._NN
        self._PC += 2
    
    def _op_add(self):
        """OPCODE add (0x7XNN): Add NN to register[X] (ignore overflows)"""
        self._register[self._X] += self._NN
        self._register[self._X] &= 0xFF
        self._PC += 2
    
    def _op_movr(self):
        """OPCODE movr(0x8XY0): Set register[X] to register[Y]"""
        self._register[self._X] = self._register[self._Y]
        self._PC += 2
    
    def _op_or(self):
        """OPCODE or (0x8XY1): OR register[Y] into register[X]"""
        self._register[self._X] |= self._register[self._Y]
        self._PC += 2
    
    def _op_and(self):
        """OPCODE and (0x8XY2): AND register[Y] into register[X]"""
        self._register[self._X] &= self._register[self._Y]
        self._PC += 2
    
    def _op_xor(self):
        """OPCODE and (0x8XY3): XOR register[Y] into register[X]"""
        self._register[self._X] ^= self._register[self._Y]
        self._PC += 2
    
    def _op_addr(self):
        """OPCODE add (0x8XY4): Add register[Y] to register[X].
        If overflow, set register[F] to 1 else 0
        
        """
        self._register[self._X] += self._register[self._Y]
        if(self._register[self._X] > 0xFF):
            self._register[self._X] &= 0xFF
            self._register[0xF] = 1
        else:
            self._register[0xF] = 0
        self._PC += 2
    
    def _op_sub(self):
        """OPCODE sub (0x8XY5): Subtract register[Y] from register[X].
        If overflow, set register[0xF] to 0 else 1
        
        """
        self._register[self._X] -= self._register[self._Y]
        if(self._register[self._X] < 0x00):
            self._register[self._X] &= 0xFF
            self._register[0xF] = 0
        else:
            self._register[0xF] = 1
        self._PC += 2
    
    def _op_shr(self):
        """OPCODE shr(0x8X06): Set register[F] to bit 0 of register[X],
        then shift register[X] right 1 bit.
        
        """
        self._register[0xF] = self._register[self._X] & 0x1
        self._register[self._X] = self._register[self._X] >> 1
        self._PC += 2
    
    def _op_rsb(self):
        """OPCODE rsb(0x8XY7): Subtract register[X] from register[Y] and
        store back in register[X], if overflow, set register[F] to 0 else 1
        
        """
        self._register[self._X] = self._register[self._Y] - \
            self._register[self._X]        
        if(self._register[self._X] < 0x00):
            self._register[self._X] &= 0xFF
            self._register[0xF] = 0
        else:
            self._register[0xF] = 1
        self._PC += 2
    
    def _op_shl(self):
        """OPCODE shl(0x8X0E): Set register[0xF] to bit 8 of register[X],
        then shift register[X] left 1 bit.
        
        """
        self._register[0xF] = self._register[self._X] & 0x80
        self._register[self._X] = self._register[self._X] << 1
        self._PC += 2
    
    def _op_skner(self):
        """OPCODE skne(0x9XY0): Skip next instruction
        if register[X] != register[Y]
        
        """
        if(self._register[self._X] != self._register[self._Y]):
            self._PC += 4
        else:
            self._PC += 2
    
    def _op_mvi(self):
        """OPCODE mvi(0xANNN): Set the address register to NNN"""
        self._addressRegister = self._NNN
        self._PC += 2
    
    def _op_jmi(self):
        """OPCODE jmi(0xBNNN): Jump to NNN + register[0]"""
        self._PC = _NNN + self._register[0x0]
    
    def _op_rand(self):
        """OPCODE rand (0xCXNN): Generate a random number anded with NN
        and store it in register[X]
        
        """
        self._register[self._X] = randint(0x0, 0xFF) & self._NN
        self._PC += 2
    
    def _op_sprite(self):
        """OPCODE sprite (0xDXYN): Draw a sprite of (8, N dimensions)
        at (register[X], register[Y]) pointed to by addressRegister.
        If a pixel is overwritten, set register[F] to 1 (default 0)
        
        """
        x = self._register[self._X]
        y = self._register[self._Y]        
        address = self._addressRegister
        self._register[0xF] = 0
        
        if(self._displayMode == 0 and self._N == 0):
            self._N = 16
        
        if(self._N != 0):
            # Normal-sized sprite
            for i in xrange(self._N):
                spriteRow = self._memory[address]
                currY = (y + i)
                
                # currY %= self._VRAMY
                # Ignore if not within screen Y range
                if(currY < 0 or currY >= self._VRAMY):
                    continue
                
                for j in xrange(8):               
                    currBit = (spriteRow >> (7 - j)) & 0x01
                    currX = (x + j)
                    # currX %= self._VRAMX
                    # Ignore if not within screen X range
                    if(currX < 0 or currX >= self._VRAMX):
                        continue
                    
                    #Ignore if bit is not set
                    if(currBit == 0):
                        continue
                    
                    if(self._VRAM[currY][currX]):
                        self._register[0xF] = 1
                        self._VRAM[currY][currX] = 0
                    else:
                        self._VRAM[currY][currX] = 1
                # Go to the next byte
                address += 1 
        else:
            # 16x16 sprite
            for i in xrange(16):
                spriteRow = (self._memory[address] << 8) + \
                                self._memory[address + 1]
                currY = (y + i)
                
                # Ignore if not within screen Y range
                if(currY < 0 or currY >= self._VRAMY):
                    continue
                
                for j in xrange(16):
                    currBit = (spriteRow >> (15 - j)) & 0x01
                    currX = (x + j)
                    
                    # Ignore if not within screen X range
                    if(currX < 0 or currX >= self._VRAMX):
                        continue
                    
                     #Ignore if bit is not set
                    if(currBit == 0):
                        continue
                    
                    if(self._VRAM[currY][currX]):
                        self._register[0xF] = 1
                        self._VRAM[currY][currX] = 0
                    else:
                        self._VRAM[currY][currX] = 1
                    
                # Go to the next byte
                address += 2 
        self._PC += 2
    
    def _op_skpr(self):
        """OPCODE skpr (0xEX9E): Skip next instruction
        if key ID in register[X] is down
        
        """
        if(self._gamepad.keyIsDown(self._register[self._X])):
            self._PC += 4
        else:
            self._PC += 2
    
    def _op_skup(self):
        """OPCODE skpr (0xEXA1): Skip next instruction
        if key ID in register[X] is up
        
        """
        if(not self._gamepad.keyIsDown(self._register[self._X])):
            self._PC += 4
        else:
            self._PC += 2    
    
    def _op_gdelay(self):
        """OPCODE gdelay (0xFX07): Set register[X] to the delay timer value"""
        self._register[self._X] = self._delayTimer
        self._PC += 2
    
    def _op_key(self):
        """OPCODE key (0xFX0A): Halt until a keypress is detected,
        then record in register[X]
        
        """
        if(self._gamepad.keyCount() == 0):
            self._halted = 1
        else:
            self._register[self._X] = self._gamepad.lastKey()
            self._halted = 0
            self._PC += 2
    
    def _op_sdelay(self):
        """OPCODE sdelay (0xFX15): Set the delay timer to register[X]"""
        self._delayTimer = self._register[self._X]
        self._PC += 2
    
    def _op_ssound(self):
        """OPCODE ssound (0xFX18): Set the sound timer to register[X]"""
        self._soundTimer = self._register[self._X]
        self._PC += 2
    
    def _op_adi(self):
        """OPCODE adi (0xFX1E): Add register[X] to the address register"""
        self._addressRegister += self._register[self._X]
        self._PC += 2
    
    def _op_nfnt(self):
        """OPCODE nfnt (0xFX29): Set the address register to the location
        of normal font data for character in register[X]
        
        """
        # Fonts are stored at 0x000 onward and take up 5 bytes each
        self._addressRegister = self._register[self._X] * 5
        self._PC += 2
    
    def _op_bcd(self):
        """OPCODE bcd(0xFX33): Convert register[X] to BCD and store each
        3 bits in memory location specified by register[addressregister]
        to register[addressregister + 2]
        
        """
        address = self._addressRegister
        number = self._register[self._X]
        # Taken from David Winter's documentation
        self._memory[address] =  number // 100
        self._memory[address + 1] = (number % 100) // 10
        self._memory[address + 2] = number % 10
        self._PC += 2
    
    def _op_str(self):
        """OPCODE str(0xFX55): Store register[0 : X] at memory[i : i + X]"""
        address = self._addressRegister
        for i in xrange(self._X + 1):
            self._memory[address] = self._register[i]
            address += 1
        self._PC += 2
    
    def _op_ldr(self):
        """OPCODE ldr(0xFX65): Load register[0 : X] from memory[i : i + X]"""
        address = self._addressRegister
        for i in xrange(self._X + 1):
            self._register[i] = self._memory[address]
            address += 1
        self._PC += 2
