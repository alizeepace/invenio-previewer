# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Test example app."""

import os
import signal
import subprocess
import sys
import time


def setup_module(module):
    """Set up before all tests."""
    # switch to examples/app.py
    exampleappdir = os.path.join(os.path.split(sys.path[0])[0],
                                 'examples')
    os.chdir(exampleappdir)


def teardown_module(module):
    """Tear down after all tests."""
    cmd = 'FLASK_APP=app.py flask db drop --yes-i-know'
    exit_status = subprocess.call(cmd, shell=True)
    assert exit_status == 0

def test_example_app():
    """Test example app."""

    # Testing database creation
    for cmd in ['mkdir -p instance',
                'pip install -r requirements.txt',
                'FLASK_APP=app.py flask db drop --yes-i-know',
                'FLASK_APP=app.py flask db init',
                'FLASK_APP=app.py flask db create']:
        exit_status = subprocess.call(cmd, shell=True)
    assert exit_status == 0

    # Testing user creation
    # TODO: is this necessary?
    cmd = 'FLASK_APP=app.py flask users create -a info@inveniosoftware.org --password 123456'
    exit_status = subprocess.call(cmd, shell=True)
    assert exit_status == 0

    # Download javascript and css libraries
    for cmd in ['FLASK_APP=app.py flask npm',
                'cd static && npm install && cd ..',
                'FLASK_APP=app.py flask collect -v',
                'FLASK_APP=app.py flask assets build',
                'FLASK_APP=app.py flask fixtures files']:
        exit_status = subprocess.call(cmd, shell=True)
    assert exit_status == 0

    # Starting example web app
    cmd = 'FLASK_APP=app.py flask run'
    webapp = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              preexec_fn=os.setsid, shell=True)
    time.sleep(5)

    # Testing record retrieval via web
    cmd = 'curl http://localhost:5000/records/5/preview?filename=markdown.md'
    output = subprocess.check_output(cmd, shell=True)
    assert 'Paragraphs are separated by a blank line.' in str(output)

    # Stopping example web app
    os.killpg(webapp.pid, signal.SIGTERM)