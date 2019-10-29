import websockets
import asyncio
import ctypes
import os
import logging
import copy
import ssl
import pathlib
from threading import Thread
import tkinter as tk

logging.basicConfig(level=logging.NOTSET)

from abc      import ABCMeta, abstractmethod
from mem_edit import Process
from time     import sleep

class SplitterState:
    split = 0
    reset = 0
    start = 0


#######################################################
class Autosplitter(tk.Frame, metaclass=ABCMeta):

    process : Process = None
    refreshRate = 30
    _state = SplitterState()
    
    # This method is called when the process is found
    @staticmethod
    @abstractmethod
    def state():
        pass

    #######################################################
    def __init__(self, master=None):
        self.master = master

        super().__init__(master)
        
    
    #######################################################
    async def _process_connection(self, websocket, path):

        _state = copy.deepcopy(self._state)
        while True:

            if self._state.start > _state.start:
                await websocket.send("start")
                _state.start += 1

            if self._state.split > _state.split:
                await websocket.send("split")
                _state.split += 1

            if self._state.reset > _state.reset:
                await websocket.send("reset")
                _state.reset += 1    
                
            await asyncio.sleep(1/self.refreshRate)
        

    #######################################################
    def _process(self):
        while True:
            sleep(2)
            pid = self.state()
            if pid is not None:
                
                with Process.open_process(pid) as self.process:

                    if not self.init():
                        continue
                    
                    while True:

                        if not process_valid(self.process):
                            self.exit()
                            break
                        
                        if self.update():

                            if self.start():
                                self._state.start += 1

                            if self.split():
                                self._state.split += 1

                            if self.reset():
                                self._state.reset += 1

                        sleep(1/self.refreshRate)
            
        pass
    
    #######################################################
    def run(self, addr, port, cert_file=None):

        thread = Thread(target = self._process)
        thread.start()

        # Setup SSL
        ssl_context = None
        if cert_file:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            pem = pathlib.Path(__file__).with_name(cert_file)
            ssl_context.load_cert_chain(pem)
        
        server = websockets.serve(self._process_connection,
                                  addr,
                                  port,
                                  ssl=ssl_context)
        
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()
        pass
    
    # This method is called when the process is found
    @abstractmethod
    def init(self):
        pass

    # This method is called when the process exits
    @abstractmethod
    def exit(self):
        pass

    # General update mthod
    @abstractmethod
    def update(self):
        pass

    # Return true for splitting
    @abstractmethod
    def split(self):
        pass

    # Return true for starting
    @abstractmethod
    def start(self):
        pass

    # Return true for resetting
    @abstractmethod
    def reset(self):
        pass
    
    pass

#######################################################
def process_valid(process : Process):
    try:
        os.kill(process.pid, 0)

    except OSError:
        return False
    else:
        return True

#######################################################
def get_module_addr(process : Process, module):
    regions = process.list_mapped_regions_by_name(
        name = module, writeable_only = False, include_anons=False
        )

    return regions[0][0] if len(regions) > 0 else 0

#######################################################
class DeepPointer:

    module = None
    offsets = []
    val_type = None
    cache = [-1, -1] # Cache for storing module address since finding that
               # takes ages
    
    #######################################################
    def __init__(self, val_type, offsets, module=None):

        self.offsets = offsets
        self.module = module
        self.val_type = val_type
    
    #######################################################
    def resolve(self, process):

        value = self.val_type()
        if process.pid == self.cache[0]:
            ptr = ctypes.c_int(self.cache[1])
        else:
            ptr = ctypes.c_int(get_module_addr(process, self.module))
            self.cache = [process.pid, ptr.value]
        
        for i, offset in enumerate(self.offsets):

            if i < len(self.offsets) - 1:
                process.read_memory(ptr.value + offset, ptr)
                
            else:
                process.read_memory(ptr.value + offset, value)

        return value.value


#######################################################
class MemoryWatcher:

    pointer = None
    current = 0
    previous = 0

    #######################################################
    def __init__(self, pointer : DeepPointer):
        self.pointer = pointer

    #######################################################
    def update(self, process : Process):

        self.previous = self.current
        self.current  = self.pointer.resolve(process)
