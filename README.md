# pynuget
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
