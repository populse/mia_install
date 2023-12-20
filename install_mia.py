# -*- coding: utf-8 -*- #
"""The first module used during mia's installation.

Basically, this module is dedicated to the initialisation of the basic
parameters and the various checks necessary for a successful installation
of mia.

:Contains:
    :Function:
        - install_package
"""

###############################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
###############################################################################

import importlib
import os
import subprocess
import sys

# We use this module only im user mode.
os.environ["MIA_DEV_MODE"] = "0"
def install_package(package):
    """Install the package if it is not already installed

     Careful: "pyyaml" in the PyPi world but "yaml" in the Python world.
    """
    try:

        if package == 'pyyaml':
            importlib.import_module('yaml')

        else:
            importlib.import_module(package)

    except ImportError:
        subprocess.call([sys.executable,
                         '-m', 'pip', 'install',
                         '--user', package])

if __name__ == '__main__':
    print('Please wait, installation in progress! ...\n')
    install_package('PyQt5')
    install_package('pyyaml')
    install_package('packaging')
    install_package('cryptography')

    try:
        import yaml

    except ImportError:  # giving a last chance to install pyyaml
        subprocess.call([sys.executable,
                         '-m', 'pip', 'install',
                         '--user', 'pyyaml'])

    try:
        from PyQt5 import QtWidgets

    except ImportError:  # giving a last chance to install PyQt5
        subprocess.call([sys.executable,
                         '-m', 'pip', 'install',
                         '--user', 'PyQt5'])

    # Removing packages from the sys modules to avoid conflicts
    keys2remove = []

    for key in sys.modules.keys():

        if key.startswith('PyQt5'):
            keys2remove.append(key)

    for key in keys2remove:
        del sys.modules[key]

    if 'yaml' in sys.modules.keys():
        del sys.modules['yaml']

    if 'packaging' in sys.modules.keys():
        del sys.modules['packaging']

    if 'cryptography' in sys.modules.keys():
        del sys.modules['cryptography']

    try:
        from PyQt5 import QtWidgets
        import yaml, packaging, crypt
        # FIXME: crypt to be replaced by legacycrypt, bcrypt, argon2-cffi,
        #        hashlib,and passlib, in python 3.13

        # If the packages needed for MIAInstallWidget are installed, we
        # can now import MIAInstallWidget
        from mia_install_widget import MIAInstallWidget

    except ImportError as e:
        sys.exit('\n{}...\n\nPython package environment has not been correctly '
                 'updated!\n\nPlease relaunch the following command:\n    '
                 'python3 install_mia.py\n\nIf the issue persists try to '
                 'install the problematic module by hand.\n'.format(e))

    app = QtWidgets.QApplication(sys.argv)
    mia_install_widget = MIAInstallWidget()

    # Setting the window to the middle of the screen
    frame_gm = mia_install_widget.frameGeometry()
    screen = QtWidgets.QApplication.desktop().screenNumber(
                            QtWidgets.QApplication.desktop().cursor().pos())
    center_point = QtWidgets.QApplication.desktop().screenGeometry(
                                                            screen).center()
    frame_gm.moveCenter(center_point)
    mia_install_widget.move(frame_gm.topLeft())

    mia_install_widget.show()
    app.exec()
