# Create a python-debian-apache image.
FROM python:3.7.1-slim-stretch

LABEL maintainer="doug.thor@gmail.com"

ENV WSGI_VERSION="4.6.5"

# Install Requirements
RUN apt-get update \
    && apt-get install -y \
        apache2 \
        apache2-dev \
        make \
        wget \
    # Install mod_wsgi from source for our specific python verison
    && wget \
        -O mod_wsgi-$WSGI_VERSION.tar.gz \
        "https://github.com/GrahamDumpleton/mod_wsgi/archive/$WSGI_VERSION.tar.gz" \
    && tar -xzf mod_wsgi-$WSGI_VERSION.tar.gz \
    && cd mod_wsgi-$WSGI_VERSION \
    && ./configure \
    && make \
    && make install \
    && cd / \
    # Cleanup
    && rm -rf mod_wsgi-$WSGI_VERSION \
    && rm mod_wsgi-$WSGI_VERSION.tar.gz \
    && apt-get remove -y apache2-dev wget make \
    && apt-get clean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 80

# Run apache in the foreground
CMD ["apache2ctl", "-D", "FOREGROUND", "-e", "info"]


# And now actually add the project-specific stuff.
COPY pynuget.conf /etc/apache2/sites-available/pynuget.conf
COPY pynuget.wsgi /var/www/wsgi/pynuget.wsgi

# Install python requirements
COPY requirements.txt /
RUN pip install -r requirements.txt \
    && rm requirements.txt

RUN pip install pynuget

RUN a2ensite pynuget \
    && a2enmod headers \
    && a2dissite 000-default.conf \
    && mkdir /var/log/pynuget \
    && chown -R www-data:www-data /var/log/pynuget

# vim: tabstop=4 shiftwidth=4 expandtab filetype=dockerfile
