import ctypes
import logging

from autosplitter import DeepPointer, MemoryWatcher, Autosplitter
from mem_edit import Process

logging.basicConfig(level=logging.NOTSET)

class GTA3Autosplitter(Autosplitter):

    watchers = {}
    offset = 0
    jp = False
    version = ""
    gameStateShift = 0
    splits = []
    
    def __init__(self):
        
        #TODO: Implement settings
        
        self.missionAddresses = [
            (0x35B75C, "Luigi's Girls"),
            (0x35B76C, "Don't Spank Ma Bitch Up"),
            (0x35B770, "Drive Misty For Me"),
            (0x35B80C, "The Crook"),
            (0x35B810, "The Thieves"),
            (0x35B814, "The Wife"),
            (0x35B818, "Her Lover"),
            (0x35B780, "Mike Lips Last Lunch"),
            (0x35B784, "Farewell 'Chunky' Lee Chong"),
            (0x35B788, "Van Heist"),
            (0x35B78C, "Cipriani's Chauffeur"),
            (0x35B79C, "Taking Out the Laundry"),
            (0x35B790, "Dead Skunk in the Trunk"),
            (0x35B838, "Turismo"),
            (0x35B794, "The Getaway"),
            (0x35B7A0, "The Pick-Up"),
            (0x35B970, "Patriot Playground"),
            (0x35B7A4, "Salvatore's Called a Meeting"),
            (0x35B7B4, "Chaperone"),
            (0x35B7B8, "Cutting the Grass"),
            (0x35B7A8, "Triads and Tribulations"),
            (0x35B774, "Pump-Action Pimp"),
            (0x35B9EC, "Diablo Destruction"),
            (0x35B778, "The Fuzz Ball"),
            (0x35B7E4, "I Scream, You Scream"),
            (0x35B7E8, "Trial By Fire"),
            (0x35B7EC, "Big'N'Veiny"),
            (0x35B9F0, "Mafia Massacre"),
            (0x35B7AC, "Blow Fish"),
            (0x35B7BC, "Bomb Da Base: Act I"),
            (0x35B7C0, "Bomb Da Base: Act II"),
            (0x35B7C4, "Last Requests"),
            (0x35B878, "Sayonara Salvatore"),
            (0x35B8D4, "Bling-Bling Scramble"),
            (0x35B87C, "Under Surveillance"),
            (0x35B8AC, "Kanbu Bust-Out"),
            (0x35B9F8, "Casino Calamity"),
            (0x35B8B0, "Grand Theft Auto"),
            (0x35B8D8, "Uzi Rider"),
            (0x35B97C, "Multistorey Mayhem"),
            (0x35B880, "Paparazzi Purge"),
            (0x35B884, "Payday For Ray"),
            (0x35B890, "Silence The Sneak"),
            (0x35B888, "Two-Faced Tanner"),
            (0x35B8B4, "Deal Steal"),
            (0x35B8B8, "Shima"),
            (0x35B8BC, "Smack Down"),
            (0x35B974, "A Ride In The Park"),
            (0x35B894, "Arms Shortage"),
            (0x35B898, "Evidence Dash"),
            (0x35B89C, "Gone Fishing"),
            (0x35B8DC, "Gangcar Round-Up"),
            (0x35B8A0, "Plaster Blaster"),
            (0x35B8E0, "Kingdom Come"),
            (0x35B8C4, "Liberator"),
            (0x35B8C8, "Waka-Gashira Wipeout!"),
            (0x35B8CC, "A Drop In The Ocean"),
            (0x35B8FC, "Grand Theft Aero"),
            (0x35B8A4, "Marked Man"),
            (0x35B900, "Escort Service"),
            (0x35B9F4, "Rumpo Rampage"),
            (0x35B924, "Uzi Money"),
            (0x35B928, "Toyminator"),
            (0x35B92C, "Rigged to Blow"),
            (0x35B930, "Bullion Run"),
            (0x35B910, "Bait"),
            (0x35B904, "Decoy"),
            (0x35B908, "Love's Disappearance"),
            (0x35B914, "Espresso-2-Go!"),
            (0x35B918, "S.A.M."),
            (0x35B948, "The Exchange"),
            (0x35B934, "Rumble"),
            (0x35B978, "Gripped!")
        ]
        
        self.refreshRate = 30
    
    #######################################################
    @staticmethod
    def state():
        return Process.get_pid_by_name('gta3.exe')

    #######################################################
    def init(self):
        
        #versionCheck10
        if DeepPointer(ctypes.c_int, [0x1C1E70]).resolve(
                self.process) == 1407551829:
            self.offset = -0x10140
            self.gameStateShift = 0
            self.version = "1.0"

        #versionCheck11
        elif DeepPointer(ctypes.c_int, [0x1C2130]).resolve(
                self.process) == 1407551829:
            self.offset = -0x10140
            self.gameStateShift = 0
            self.version = "1.1"
        
        #versionCheckJP
        elif DeepPointer(ctypes.c_int, [0x1B52D0]).resolve(
                self.process) == 1407551829:
            self.offset = -0x21E0
            self.jp = True
            self.gameStateShift = 4
            self.version = "JP"

        else:
            self.version = ""
            return False

        print("Attached to GTA 3 v%s" % self.version)
            
        # Adds mission memory addresses (with the correct offset) to the
        # watcher list.
        for address in self.missionAddresses:
            self.watchers[address[1]] = MemoryWatcher(
                DeepPointer(ctypes.c_int, [address[0] + self.offset])
            )

        self.watchers["gameState"] = MemoryWatcher(
            DeepPointer(ctypes.c_int,
                        [0x50387C if self.jp else 0x505A2C + self.offset])
        )
        
        return True
        pass

    #######################################################
    def update(self):

        if self.version == "":
            return False
        
        for watcher in self.watchers.values():
            watcher.update(self.process)

        return True
    
    #######################################################
    def split(self):

        #TODO: On starting missions
        #TODO: Collectibles
        for offset, mission in self.missionAddresses:

            if self.watchers[mission].current > self.watchers[mission].previous \
               and mission not in self.splits:
                
                self.splits.append(mission)
                return True
        
        pass
    
    #######################################################
    def start(self):

        # GTA3-NEW.asl uses a different method, but that can't be used here
        # because it's not possible to get the timer through the websockets
        if self.watchers["gameState"].previous == 8 and \
            self.watchers["gameState"].current == 9:
            self.splits = []
            return True

        return False

    #######################################################
    def exit(self):
        pass
    
    #######################################################
    def reset(self):
        return self.watchers["gameState"].previous == 9 and \
            self.watchers["gameState"].current == 8
    pass

GTA3Autosplitter().run("localhost", 8765, "out.pem")
