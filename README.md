
# ollama-matrix-client
A matrix client that connects with Ollama.
Inspired by https://github.com/h1ddenpr0cess20/ollamarama-matrix.git but using Ollama-python's library as opposed to litellm and trying to create a daemon, Pypi Package and Docker release.
[![Built with matrix-nio](https://img.shields.io/badge/built%20with-matrix--nio-brightgreen)](https://github.com/poljar/matrix-nio)

This is a simple application that connects to a Matrix Homeserver configured in the config.yaml file, then monitors the predefined room or rooms on the config file and sends the messages (in plain text) to Ollama.

To install

The script requires:

python and pip to be installed on the server 
for linux (apt):
```
sudo apt install python3 python3-pip git python3-yaml python3-daemon libolm-dev
```
as well as the following modules with pip:

yaml, ollama, matrix-nio and python-daemon:
```
sudo pip install pyyaml ollama matrix-nio[e2e] python-daemon 
```
alternatively, in some distros (such as ubuntu) you can install the following packages from apt but still need to install ollama:

python3-matrix-nio python3-yaml python3-daemon

Once installed, just copy this repo (you can use git clone), complete the YAML file and rename it config.yaml in the ollama-matrix/config/ folder, make the script executable and run it.

That's it. You can execute it with -d in order to have the script run as a daemon. 


All of the configuration is done via a config.yaml file, an example file is provided, you need to rename it to config.yml.  You can also execute with -c for an interactive prompt of each config item.

It must contain:

A MATRIX dictionary, which will be the Matrix configuration with HOMESERVER, USER, PASSWORD and a list of ROOMS the bot will connect to, the user has to have been created first in your homeserver and invited to the rooms:
```
MATRIX:
    HOMESERVER: homeserver.host.com
    USER: 'MATRIXUSER'
    PASSWORD: 'MATRIXPASSWORD' 
    ROOMS:        #The list of rooms your bot will be in
              - ROOM: "#test:homeserver.host.com"
              - ROOM: "#ROOM2:homeserver.host.com"
```

An OLLAMA dictionary, which will be the Ollama-python configuration, which a HOST and a MODEL entry:

```
OLLAMA:
    HOST: 192.168.XXX.XXX # the host for the Ollama API
    MODEL: 'ollama/llama3' #the model you want to use
```

