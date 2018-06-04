# -*- coding: utf-8 -*-
"""
"""
import os


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def check_push(expected_code, client, header, file=None):
    data = None
    if file:
        nupkg_file = os.path.join(DATA_DIR, file)
        openf = open(nupkg_file, 'rb')
        data = {'package': (openf, 'filename.nupkg')}

    rv = client.put(
        '/api/v2/package/',
        headers=header,
        follow_redirects=True,
        data=data,
    )

    try:
        openf.close()
    except Exception:
        pass

    assert rv.status_code == expected_code
