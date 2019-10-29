# Websocket-based Autosplitter for LiveSplit

This repository contains a base class that can be inherited from other classes to ease creating autosplitters and a sample GTA 3 Autosplitter that splits upon mission completion.

## Usage

### Prerequisites

The base class requires the following packages to be installed.

- Python 3
- [websockets](https://pypi.org/project/websockets/)
- [mem_edit](https://github.com/Zarig/mem_edit)

Both of the above can be installed by running the following command:
`pip install -r requirements.txt`

### SSL Context

An SSL Context is required for connection to the websockets from major browsers. For this reason, you'll need a certificate file to authenticate the connection. A script to generate a self signed certificate has been provided with the repository and can be run by `./generate_cert.sh`. You require `openssl` to run the script.

Alternatively, you can set Firefox to allow insecure websockets by setting this to true in about:config, `network.websocket.allowInsecureFromHTTPS`. If you do this, you'll need to edit the sample autosplitter and remove `,"out.pem"` from the last line.

### Running

You will require root privileges to read the memory of a wine process. Other processes may or may not require such permissions, depending upon the method of execution.

To run the GTA3 autosplitter:
`sudo python gta3.py`

### Connecting

Before connecting, you'll have to add an exception for the self-signed certificate. To do that, visit `https://servername:port` (Where servername and port are the arguments passed to the run function in the autosplitter, `localhost:8765` in the GTA3 autosplitter). The browser should display a warning about the self signed certificate, for which you can add an exception from there.

After running the autosplitter, you'll have to connect to `wss://servername:port` from LiveSplitOne. 

You can have multiple connections to the same websocket from multiple devices. (Note: To connect from different devices on the same network, you'll have to modify the servername to be the local ip-address of the host PC).
