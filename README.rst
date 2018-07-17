=======
pynuget
=======

.. image:: https://img.shields.io/travis/dougthor42/pynuget.svg
   :alt: Travis
   :target: https://travis-ci.org/dougthor42/pynuget

A port of https://github.com/Daniel15/simple-nuget-server/ because I
don't know PHP or Nginx. Runs on Flask and Apache. Python 3.5+


Installation
------------


1. Install the Prerequisites
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    $ sudo apt install apache2
    $ sudo apt install libapache2-mod-wsgi-py3



2. Create a Virtual Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    $ python3 -m venv /usr/local/venv-pynuget/        # or anywhere
    $ . /usr/local/venv-pynuget/bin/activate


3. Install the Package
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    $ pip install pynuget



4. Run the Initial Setup Script
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    $ sudo -E /usr/local/venv-pynuget/bin/pynuget init

.. important::

    Note the ``-E`` flag on ``sudo``! This preserves environment variables.
    We're specifically interested in the ``VIRTUAL_ENV`` variable, as that's
    needed to update the WSGI file.

.. note::

    TODO: Instructions for a system install.

+ Sorry that this needs sudo! I haven't come up with a better way
  around this. Suggestions or PRs welcome!
+ This will do various things including but not limited to:
    + Creating ``/var/www/pynuget``, populating it with the WSGI file and
      repository folders and adjusting permissions
    + Copying over the example apache config and enabling the site
    + Restarting apache


5. Test Things
^^^^^^^^^^^^^^

1. ``curl localhost`` should return a short blurb about nuget
2. On Windows::

    nuget.exe push Foo.nupkg -ApiKey YourApiKey -Source http://your.server.com

3. On Linux with Mono::

    mono /path/to/nuget.exe push Foo.nupkg -ApiKey YourApiKey -Source http://your.server.address

4. If your server has a Window manager, you can open up a web browser and
   navigate to ``http://localhost`` and you should see the PyNuGet landing
   page.
