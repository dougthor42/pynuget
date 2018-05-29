# pynuget

![Travis](https://img.shields.io/travis/dougthor42/pynuget.svg)

A port of https://github.com/Daniel15/simple-nuget-server/ because I
don't know PHP or Nginx. Runs on Flask and Apache. Python 3.5+

## Installation
1.  `sudo apt install apache2`
2.  `sudo apt install libapache2-mod-wsgi
3.  (Optional, but recommended) Create a virtual env that the app will run
    in: `python3 -m venv /usr/local/pynuget-venv` and then activate it:
    `. /urs/local/pynuget-venv/bin/activate`
4.  Install PyNuGet: `pip install pynuget`
5.  Run the initial setup script: `sudo pynuget init`
    + This will do various things including but not limited to:
        + Creating `/var/www/pynuget`, populating it with the WSGI file and
          repository folders and adjusting permissions
        + Copying over the example apache config and enabling the site
        + Restarting apache
6.  Test things:
    1. `curl localhost` should return a short blurb about nuget
    2. (On Windows or via Mono) `nuget.exe setApiKey -Source http://your.server.com
       yourApiKey` and then `nuget.exe push Foo.nupkg -Source
       http://your.server.com`


## Testing

### Prerequisites:

This has been tested on Ubuntu 16.04.4 and Windows 10 WSL (Ubuntu 16.04)

The Ubuntu repo for Mono has v4.2.1. We want a higher version of Mono.

1.  Follow directions
    [here](http://www.mono-project.com/download/stable/#download-lin) but
    remove the `:80` from the keyserver URL.
2.  Install Mono-complete: `sudo apt install mono-complete`
3.  Download NuGet: `wget https://dist.nuget.org/win-x86-commandline/v4.6.2/nuget.exe`
4.  Check things: `mono /path/to/nuget.exe`


### Running Tests:

Clone the repo and install the development requirements:

1.  `git clone git@github.com:dougthor42/pynuget.git`
2.  `cd pynuget`
3.  `python -m venv .venv`
4.  `. .venv/bin/activate`
5.  `pip install -r requirements.txt`
6.  `pip install -r requirements-dev.txt`
7.  `pytest`
