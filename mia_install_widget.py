# -*- coding: utf-8 -*- #
"""The module used for mia's installation and configuration.

Basically, this module is dedicated to the GUI used at the installation time

:Contains:
    :Class:
        - MIAInstallWidget


"""

###############################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
###############################################################################


import os
import shutil
import subprocess
import sys
import tempfile
import yaml
from cryptography.fernet import Fernet
from packaging import version
from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore

CONFIG = b'5YSmesxZ4ge9au2Bxe7XDiQ3U5VCdLeRdqimOOggKyc='


class MIAInstallWidget(QtWidgets.QWidget):
    """The main class for mia's installation and configuration.

    :Contains:
        :Method:
            - __init__
            - browse_matlab
            - browse_matlab_standalone
            - browse_mia_config_path
            - browse_projects_path
            - browse_spm
            - browse_spm_standalone
            - btnstate
            - clone_miaResources
            - find_matlab_path
            - install
            - install_matlab_api
            - install_package
            - last_layout
#            - load_config
            - make_mrifilemanager_folder
#            - make_populse_mia_folder
            - ok_or_abort
#            - save_config
            - set_new_layout
            - uninstall_package
            - upgrade_soma_capsul
            - use_matlab_changed
            - use_spm_changed
            - use_spm_standalone_changed
    """

    def __init__(self):
        super().__init__()

        self.matlab_path = ""

        # Labels
        # self.top_label_text = ''
        # self.top_label = QtWidgets.QLabel(self.top_label_text)
        #
        # self.top_label_font = QtGui.QFont()
        # self.top_label_font.setBold(True)
        # self.top_label.setFont(self.top_label_font)
        #
        # h_box_top_label = QtWidgets.QHBoxLayout()
        # h_box_top_label.addStretch(1)
        # h_box_top_label.addWidget(self.top_label)
        # h_box_top_label.addStretch(1)

        self.middle_label_text = ("Please select a configuration installation "
                                  "path, a folder to store the projects and "
                                  "the paths to run Matlab and SPM.\nThe "
                                  "paths to Matlab and SPM can then be "
                                  "modified in the Mia preferences.\n\n"
                                  )
        self.middle_label = QtWidgets.QLabel(self.middle_label_text)
        h_box_middle_label = QtWidgets.QHBoxLayout()
        h_box_middle_label.addStretch(1)
        h_box_middle_label.addWidget(self.middle_label)
        h_box_middle_label.addStretch(1)

        # Groupbox
        self.groupbox = QtWidgets.QGroupBox()
        self.mia_config_path_label = QtWidgets.QLabel("Mia configuration path:")
        self.mia_config_path_choice = QtWidgets.QLineEdit(os.path.join(
                                                    os.path.expanduser('~'),
                                                    '.populse_mia')
                               )
        self.mia_config_path_browse = QtWidgets.QPushButton("Browse")
        self.mia_config_path_browse.clicked.connect(self.browse_mia_config_path)

        self.mia_config_path_info = QtWidgets.QPushButton(" ? ")
        self.mia_config_path_info.setFixedHeight(27)
        self.mia_config_path_info.setFixedWidth(27)
        self.mia_config_path_info.setStyleSheet("background-color:rgb(150,150,200)")
        rect = QtCore.QRect(4, 4, 17, 17)
        region = QtGui.QRegion(rect, QtGui.QRegion.Ellipse)
        self.mia_config_path_info.setMask(region)
        tool_tip_message = ("Three folders will be created in the selected "
                            "folder:\n"
                            "- usr/properties: containing Mia's configuration "
                            "and resources files.\n"
                            "- usr/processes: containing personal pipelines "
                            "and bricks.\n"
                            "- usr/MRIFileManager: containing the data "
                            "converter used in Mia.\n"
                            "- usr/MiaResources: containing reference data "
                            "(ROI, templates, etc.)")
        self.mia_config_path_info.setToolTip(tool_tip_message)

        h_box_mia_config = QtWidgets.QHBoxLayout()
        h_box_mia_config.addWidget(self.mia_config_path_choice)
        h_box_mia_config.addWidget(self.mia_config_path_browse)
        h_box_mia_config.addWidget(self.mia_config_path_info)

        v_box_mia_config = QtWidgets.QVBoxLayout()
        v_box_mia_config.addWidget(self.mia_config_path_label)
        v_box_mia_config.addLayout(h_box_mia_config)

        projects_path_default = ''  # setting a default value for the projects?

        self.projects_path_label = QtWidgets.QLabel("Mia projects path:")
        self.projects_path_choice = QtWidgets.QLineEdit(projects_path_default)
        self.projects_path_browse = QtWidgets.QPushButton("Browse")
        self.projects_path_browse.clicked.connect(self.browse_projects_path)

        self.projects_path_info = QtWidgets.QPushButton(" ? ")
        self.projects_path_info.setFixedHeight(27)
        self.projects_path_info.setFixedWidth(27)
        self.projects_path_info.setStyleSheet("background-color:"
                                              "rgb(150,150,200)")
        rect = QtCore.QRect(4, 4, 17, 17)
        region = QtGui.QRegion(rect, QtGui.QRegion.Ellipse)
        self.projects_path_info.setMask(region)
        tool_tip_message = ('A "projects" folder will be created in this '
                            'specified folder.')
        self.projects_path_info.setToolTip(tool_tip_message)

        h_box_projects_path = QtWidgets.QHBoxLayout()
        h_box_projects_path.addWidget(self.projects_path_choice)
        h_box_projects_path.addWidget(self.projects_path_browse)
        h_box_projects_path.addWidget(self.projects_path_info)

        v_box_projects_path = QtWidgets.QVBoxLayout()
        v_box_projects_path.addWidget(self.projects_path_label)
        v_box_projects_path.addLayout(h_box_projects_path)

        v_box_paths = QtWidgets.QVBoxLayout()
        v_box_paths.addLayout(v_box_mia_config)
        v_box_paths.addLayout(v_box_projects_path)

        self.groupbox.setLayout(v_box_paths)

        # Installation target groupbox
        self.install_target_group_box = QtWidgets.QGroupBox('Installation target:')

        self.casa_target_push_button = QtWidgets.QRadioButton(
            'Casa_Distro')
        self.casa_target_push_button.toggled.connect(
            lambda: self.btnstate(self.casa_target_push_button))
        self.host_target_push_button = QtWidgets.QRadioButton(
            'Host')
        self.host_target_push_button.setChecked(True)
        self.host_target_push_button.toggled.connect(
            lambda: self.btnstate(self.host_target_push_button))

        v_box_install_target = QtWidgets.QVBoxLayout()
        v_box_install_target.addWidget(self.casa_target_push_button)
        v_box_install_target.addWidget(self.host_target_push_button)

        self.install_target_group_box.setLayout(v_box_install_target)

        h_box_install_target = QtWidgets.QVBoxLayout()
        h_box_install_target.addWidget(self.install_target_group_box)
        h_box_install_target.addStretch(1)

        # Clinical mode groupbox
        self.clinical_mode_group_box = QtWidgets.QGroupBox('Operating mode:')

        self.clinical_mode_push_button = QtWidgets.QRadioButton('Clinical mode')
        self.clinical_mode_push_button.toggled.connect(
            lambda: self.btnstate(self.clinical_mode_push_button))

        v_box_clinical_mode = QtWidgets.QVBoxLayout()
        v_box_clinical_mode.addWidget(self.clinical_mode_push_button)

        self.clinical_mode_group_box.setLayout(v_box_clinical_mode)

        h_box_clinical_mode = QtWidgets.QVBoxLayout()
        h_box_clinical_mode.addWidget(self.clinical_mode_group_box)
        h_box_clinical_mode.addStretch(1)

        # Push buttons
        self.push_button_install = QtWidgets.QPushButton("Install")
        self.push_button_install.clicked.connect(self.install)

        self.push_button_cancel = QtWidgets.QPushButton("Cancel")
        self.push_button_cancel.clicked.connect(self.close)

        h_box_buttons = QtWidgets.QHBoxLayout()
        h_box_buttons.addStretch(1)
        h_box_buttons.addWidget(self.push_button_install)
        h_box_buttons.addWidget(self.push_button_cancel)

        # Matlab and SPM12 groupboxes

        # Groupbox "Matlab"
        self.groupbox_matlab = QtWidgets.QGroupBox("Matlab")
        self.use_matlab_label = QtWidgets.QLabel("Use Matlab")
        self.use_matlab_checkbox = QtWidgets.QCheckBox('', self)

        matlab_path = self.find_matlab_path()
        self.matlab_label = QtWidgets.QLabel("Matlab path:")
        self.matlab_choice = QtWidgets.QLineEdit(matlab_path)
        self.matlab_browse = QtWidgets.QPushButton("Browse")
        self.matlab_browse.clicked.connect(self.browse_matlab)

        self.matlab_standalone_label = QtWidgets.QLabel("Matlab standalone "
                                                        "path:")
        self.matlab_standalone_choice = QtWidgets.QLineEdit()
        self.matlab_standalone_browse = QtWidgets.QPushButton("Browse")
        self.matlab_standalone_browse.clicked.connect(
            self.browse_matlab_standalone)

        h_box_use_matlab = QtWidgets.QHBoxLayout()
        h_box_use_matlab.addWidget(self.use_matlab_checkbox)
        h_box_use_matlab.addWidget(self.use_matlab_label)
        h_box_use_matlab.addStretch(1)

        h_box_matlab_path = QtWidgets.QHBoxLayout()
        h_box_matlab_path.addWidget(self.matlab_choice)
        h_box_matlab_path.addWidget(self.matlab_browse)

        v_box_matlab_path = QtWidgets.QVBoxLayout()
        v_box_matlab_path.addWidget(self.matlab_label)
        v_box_matlab_path.addLayout(h_box_matlab_path)

        h_box_matlab_standalone_path = QtWidgets.QHBoxLayout()
        h_box_matlab_standalone_path.addWidget(self.matlab_standalone_choice)
        h_box_matlab_standalone_path.addWidget(self.matlab_standalone_browse)

        v_box_matlab_standalone_path = QtWidgets.QVBoxLayout()
        v_box_matlab_standalone_path.addWidget(self.matlab_standalone_label)
        v_box_matlab_standalone_path.addLayout(h_box_matlab_standalone_path)

        v_box_matlab = QtWidgets.QVBoxLayout()
        v_box_matlab.addLayout(h_box_use_matlab)
        v_box_matlab.addLayout(v_box_matlab_path)
        v_box_matlab.addLayout(v_box_matlab_standalone_path)

        self.groupbox_matlab.setLayout(v_box_matlab)

        # Groupbox "SPM"
        self.groupbox_spm = QtWidgets.QGroupBox("SPM")

        self.use_spm_label = QtWidgets.QLabel("Use SPM")
        self.use_spm_checkbox = QtWidgets.QCheckBox('', self)

        self.spm_label = QtWidgets.QLabel("SPM path:")
        self.spm_choice = QtWidgets.QLineEdit()
        self.spm_browse = QtWidgets.QPushButton("Browse")
        self.spm_browse.clicked.connect(self.browse_spm)

        h_box_use_spm = QtWidgets.QHBoxLayout()
        h_box_use_spm.addWidget(self.use_spm_checkbox)
        h_box_use_spm.addWidget(self.use_spm_label)
        h_box_use_spm.addStretch(1)

        h_box_spm_path = QtWidgets.QHBoxLayout()
        h_box_spm_path.addWidget(self.spm_choice)
        h_box_spm_path.addWidget(self.spm_browse)

        v_box_spm_path = QtWidgets.QVBoxLayout()
        v_box_spm_path.addWidget(self.spm_label)
        v_box_spm_path.addLayout(h_box_spm_path)

        self.use_spm_standalone_label = QtWidgets.QLabel("Use SPM standalone")
        self.use_spm_standalone_checkbox = QtWidgets.QCheckBox('', self)

        self.spm_standalone_label = QtWidgets.QLabel("SPM standalone path:")
        self.spm_standalone_choice = QtWidgets.QLineEdit()
        self.spm_standalone_browse = QtWidgets.QPushButton("Browse")
        self.spm_standalone_browse.clicked.connect(self.browse_spm_standalone)

        h_box_use_spm_standalone = QtWidgets.QHBoxLayout()
        h_box_use_spm_standalone.addWidget(self.use_spm_standalone_checkbox)
        h_box_use_spm_standalone.addWidget(self.use_spm_standalone_label)
        h_box_use_spm_standalone.addStretch(1)

        h_box_spm_standalone_path = QtWidgets.QHBoxLayout()
        h_box_spm_standalone_path.addWidget(self.spm_standalone_choice)
        h_box_spm_standalone_path.addWidget(self.spm_standalone_browse)

        v_box_spm_standalone_path = QtWidgets.QVBoxLayout()
        v_box_spm_standalone_path.addWidget(self.spm_standalone_label)
        v_box_spm_standalone_path.addLayout(h_box_spm_standalone_path)

        v_box_spm = QtWidgets.QVBoxLayout()
        v_box_spm.addLayout(h_box_use_spm)
        v_box_spm.addLayout(v_box_spm_path)
        v_box_spm.addLayout(h_box_use_spm_standalone)
        v_box_spm.addLayout(v_box_spm_standalone_path)

        self.groupbox_spm.setLayout(v_box_spm)

        # Final layout

        qradiobutton_layout = QtWidgets.QVBoxLayout()
        qradiobutton_layout.addLayout(h_box_install_target)
        qradiobutton_layout.addLayout(h_box_clinical_mode)

        h_box_mode_paths = QtWidgets.QHBoxLayout()
        h_box_mode_paths.addLayout(qradiobutton_layout)
        h_box_mode_paths.addWidget(self.groupbox)

        h_box_matlab_spm = QtWidgets.QHBoxLayout()
        h_box_matlab_spm.addWidget(self.groupbox_matlab)
        h_box_matlab_spm.addWidget(self.groupbox_spm)

        self.global_layout = QtWidgets.QVBoxLayout()
        # self.global_layout.addLayout(h_box_top_label)
        self.global_layout.addLayout(h_box_middle_label)
        self.global_layout.addStretch(1)
        self.global_layout.addLayout(h_box_mode_paths)
        self.global_layout.addLayout(h_box_matlab_spm)
        self.global_layout.addLayout(h_box_buttons)

        self.setLayout(self.global_layout)
        self.setWindowTitle("MIA installation")

        # Setting the checkbox values
        if matlab_path == "":
            self.matlab_choice.setDisabled(True)
            self.matlab_standalone_choice.setDisabled(True)
            self.matlab_label.setDisabled(True)
            self.matlab_standalone_label.setDisabled(True)
            self.matlab_browse.setDisabled(True)
            self.matlab_standalone_browse.setDisabled(True)
        else:
            self.install_matlab_api()
            self.use_matlab_checkbox.setChecked(True)
        self.spm_choice.setDisabled(True)
        self.spm_standalone_choice.setDisabled(True)
        self.spm_label.setDisabled(True)
        self.spm_standalone_label.setDisabled(True)
        self.spm_browse.setDisabled(True)
        self.spm_standalone_browse.setDisabled(True)
        self.use_spm_checkbox.setChecked(False)
        self.use_spm_standalone_checkbox.setChecked(False)

        # Signals
        self.use_matlab_checkbox.stateChanged.connect(self.use_matlab_changed)
        self.use_spm_checkbox.stateChanged.connect(self.use_spm_changed)
        self.use_spm_standalone_checkbox.stateChanged.connect(
            self.use_spm_standalone_changed)

    def browse_matlab(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Choose Matlab executable file',
            os.path.expanduser('~'))[0]

        if fname:
            self.matlab_choice.setText(fname)

    def browse_matlab_standalone(self):
        fname = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            'Choose MCR directory',
            os.path.expanduser('~'))

        if fname:
            self.matlab_standalone_choice.setText(fname)

    def browse_mia_config_path(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            'Select a folder where to install Populse_MIA',
            os.path.expanduser('~'))

        if folder_name:
            self.mia_config_path_choice.setText(folder_name)

    def browse_projects_path(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select a folder where to store Populse_MIA's projects",
            os.path.expanduser('~'))

        if folder_name:
            self.projects_path_choice.setText(folder_name)

    def browse_spm(self):
        fname = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            'Choose SPM directory',
            os.path.expanduser('~'))

        if fname:
            self.spm_choice.setText(fname)

    def browse_spm_standalone(self):
        fname = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            'Choose SPM standalone directory',
            os.path.expanduser('~'))

        if fname:
            self.spm_standalone_choice.setText(fname)

    def btnstate(self, button):

        if button.text() == "Casa_Distro":

            if button.isChecked() == True:
                self.host_target_push_button.setChecked(False)

            else:
                self.host_target_push_button.setChecked(True)

        if button.text() == "Host":

            if button.isChecked() == True:
                self.casa_target_push_button.setChecked(False)

            else:
                self.casa_target_push_button.setChecked(True)

    def find_matlab_path(self):
        return_value = ""

        try:
            out = subprocess.check_output(['matlab', '-nodisplay', '-nosplash',
                                           '-nodesktop', '-r',
                                           'disp(matlabroot);exit'])
            out_split = out.split()
            valid_lines = [line for line in out_split if os.path.isdir(line)]

            if len(valid_lines) == 1:
                return_value = os.path.join(valid_lines[0].decode('ascii'),
                                            'bin', 'matlab')

                if os.path.isfile(os.path.join(valid_lines[0].decode('ascii'),
                                               'bin', 'matlab')):
                    self.matlab_path = valid_lines[0].decode('ascii')
                    return_value = os.path.join(valid_lines[0].decode('ascii'),
                                                'bin', 'matlab')

                elif os.path.isfile(os.path.join(valid_lines[0].decode('ascii'),
                                                 'bin', 'matlab.exe')):
                    self.matlab_path = valid_lines[0].decode('ascii')
                    return_value = os.path.join(valid_lines[0].decode('ascii'),
                                                'bin', 'matlab.exe')
                else:
                    return_value = ""

        # except Exception as e:
        except Exception:
            # print('\n{0}: {1}\n'.format(e.__class__, e))
            print("\nThe matlab path could not be determined "
                  "automatically ...\n")
            pass

        return return_value

    def install(self):

        # Installing Populse_mia and mia_processes from pypi
        self.install_package('populse_mia')

        from populse_mia.utils import verCmp
        from populse_mia.software_properties import Config

        # Flag used later
        self.folder_exists_flag = False

        # Checking which installation target has been selected
        if self.host_target_push_button.isChecked():
            host_target_install = True

        else:
            host_target_install = False

        # Checking which operating mode has been selected
        if self.clinical_mode_push_button.isChecked():
            use_clinical_mode = True
            self.operating_mode = "clinical"

        else:
            use_clinical_mode = False
            self.operating_mode = "research"

        if self.use_matlab_checkbox.isChecked():
            use_matlab = True
            matlab = self.matlab_choice.text()
            matlab_standalone = self.matlab_standalone_choice.text()

        else:
            use_matlab = False
            matlab = ""
            matlab_standalone = ""

        if self.use_spm_checkbox.isChecked():
            use_spm = True
            spm = self.spm_choice.text()

        else:
            use_spm = False
            spm = ""

        if self.use_spm_standalone_checkbox.isChecked():
            use_spm_standalone = True
            spm_standalone = self.spm_standalone_choice.text()

        else:
            use_spm_standalone = False
            spm_standalone = ""

        # The directory in which the configuration is located must be
        # declared in ~/.populse_mia/configuration_path.yml
        dot_mia_config = os.path.join(os.path.expanduser("~"),
                                      ".populse_mia",
                                      "configuration_path.yml"
        )
        # ~/.populse_mia/configuration_path.yml management/initialisation
        if not os.path.exists(os.path.dirname(dot_mia_config)):
            os.mkdir(os.path.dirname(dot_mia_config))
            print(
                "\nThe {0} directory is created "
                "...".format(os.path.dirname(dot_mia_config))
            )
            Path(os.path.join(dot_mia_config)).touch()

        if not os.path.exists(dot_mia_config):
            Path(os.path.join(dot_mia_config)).touch()

        # We try to keep the old values in dot_mia_config file
        with open(dot_mia_config, "r") as stream:

            try:

                if verCmp(yaml.__version__, "5.1", "sup"):
                    mia_home_properties_path = yaml.load(
                        stream, Loader=yaml.FullLoader
                    )

                else:
                    mia_home_properties_path = yaml.load(stream)

                if mia_home_properties_path is None or not isinstance(
                        mia_home_properties_path, dict
                ):
                    mia_home_properties_path = dict()

            except yaml.YAMLError:
                mia_home_properties_path = dict()

        mia_home_properties_path_new = dict()

        properties_path = self.mia_config_path_choice.text()

        if properties_path.endswith(os.sep):
            properties_path = properties_path[:-1]
            self.mia_config_path_choice.setText(properties_path)

        properties_path = os.path.join(properties_path, "usr")

        # properties folder management / initialisation:
        properties_dir = os.path.join(properties_path, "properties")

        if not os.path.exists(properties_dir):
            os.makedirs(properties_dir, exist_ok=True)
            print("\nThe {0} directory is created...".format(properties_dir))

        if not os.path.exists(
                os.path.join(properties_dir, "saved_projects.yml")
        ):
            with open(os.path.join(properties_dir,
                                   "saved_projects.yml"),
                      "w",
                      encoding="utf8") as configfile:
                yaml.dump(
                    {"paths": []},
                    configfile,
                    default_flow_style=False,
                    allow_unicode=True,
                )

            print(
                "\nThe {0} file is created...".format(
                    os.path.join(properties_dir, "saved_projects.yml")
                )
            )

        if not os.path.exists(os.path.join(properties_dir, "config.yml")):

            with open(os.path.join(properties_dir, "config.yml"),
                      "w",
                      encoding="utf8") as configfile:
                yaml.dump(
                    "gAAAAABd79UO5tVZSRNqnM5zzbl0KDd7Y98KCSKCNizp9aDq"
                    "ADs9dAQHJFbmOEX2QL_jJUHOTBfFFqa3OdfwpNLbvWNU_rR0"
                    "VuT1ZdlmTYv4wwRjhlyPiir7afubLrLK4Jfk84OoOeVtR0a5"
                    "a0k0WqPlZl-y8_Wu4osHeQCfeWFKW5EWYF776rWgJZsjn3fx"
                    "Z-V2g5aHo-Q5aqYi2V1Kc-kQ9ZwjFBFbXNa1g9nHKZeyd3ve"
                    "6p3RUSELfUmEhS0eOWn8i-7GW1UGa4zEKCsoY6T19vrimiuR"
                    "Vy-DTmmgzbbjGkgmNxB5MvEzs0BF2bAcina_lKR-yeICuIqp"
                    "TSOBfgkTDcB0LVPBoQmogUVVTeCrjYH9_llFTJQ3ZtKZLdeS"
                    "tFR5Y2I2ZkQETi6m-0wmUDKf-KRzmk6sLRK_oz6GmuTAN8A5"
                    "1au2v1M=",
                    configfile,
                    default_flow_style=False,
                    allow_unicode=True,
                )

            print(
                "\nThe {0} file is created...".format(
                    os.path.join(properties_dir, "config.yml")
                )
            )

            # processes/User_processes folder management / initialisation:
            user_processes_dir = os.path.join(
                properties_path, "processes", "User_processes"
            )

            if not os.path.exists(user_processes_dir):
                os.makedirs(user_processes_dir, exist_ok=True)
                print(
                    "\nThe {0} directory is created...".format(
                        user_processes_dir
                    )
                )

            if not os.path.exists(
                    os.path.join(user_processes_dir, "__init__.py")
            ):
                Path(
                    os.path.join(
                        user_processes_dir,
                        "__init__.py",
                    )
                ).touch()
                print(
                    "\nThe {0} file is created...".format(
                        os.path.join(properties_dir, "config.yml")
                    )
                )

        #########################
        # dot_mia_path = os.path.join(os.path.expanduser('~'), '.populse_mia')
        #
        # if not os.path.isdir(dot_mia_path):
        #     os.mkdir(dot_mia_path)
        #
        # # Checking that the specified paths are correct
        # mia_path = self.mia_config_path_choice.text()
        #
        # if not os.path.isdir(mia_path):
        #     message = ("The selected path for populse_mia must be "
        #                "an existing folder")
        #     msg = QtWidgets.QMessageBox()
        #     msg.setIcon(QtWidgets.QMessageBox.Warning)
        #     msg.setText("Populse_MIA path is not valid")
        #     msg.setInformativeText(message)
        #     msg.setWindowTitle("Warning")
        #     msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        #     msg.buttonClicked.connect(msg.close)
        #     msg.exec()
        #     return

        # project folder management / initialisation:
        projects_path = os.path.join(self.projects_path_choice.text(),
                                     "projects_mia")

        if not os.path.isdir(projects_path):
            os.makedirs(projects_path, exist_ok=True)
            print(
                "\nThe {0} directory is created...".format(
                    projects_path
                )
            )

            if len(os.listdir(projects_path)) != 0:
                message = ('The {} folder already contains data!'.format(
                    projects_path))
                self.msg = QtWidgets.QMessageBox()
                self.msg.setIcon(QtWidgets.QMessageBox.Warning)
                self.msg.setText(message)
                self.msg.setInformativeText("Hit 'OK' to overwrite this "
                                            "folder and its contents.\nPress "
                                            "'Cancel' to continue with the "
                                            "installation, retaining the "
                                            "contents of the folder.")
                self.msg.setWindowTitle("Warning")
                self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok |
                                            QtWidgets.QMessageBox.Cancel)
                self.msg.buttonClicked.connect(self.ok_or_abort)
                self.msg.exec()

            # If the user has clicked on "Cancel" we do nothing. If he clicks
            # OK, we delete the entire contents of the folder
            if not self.folder_exists_flag:

                for elmt in os.listdir(projects_path):
                    elmt_path = os.path.join(projects_path, elmt)

                    try:

                        if os.path.isfile(elmt_path) or os.path.islink(
                                elmt_path):
                            os.remove(elmt_path)

                        elif os.path.isdir(elmt_path):
                            shutil.rmtree(elmt_path)

                    except Exception as e:
                        print('Failed to delete {0}. Reason: {1}'.format(
                            elmt_path, e))


            # message = ("The selected path for populse_mia's projects "
            #            "must be an existing folder")
            # msg = QtWidgets.QMessageBox()
            # msg.setIcon(QtWidgets.QMessageBox.Warning)
            # msg.setText("Populse_MIA's projects path is not valid")
            # msg.setInformativeText(message)
            # msg.setWindowTitle("Warning")
            # msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            # msg.buttonClicked.connect(msg.close)
            # msg.exec()
            # return

        # if os.path.isdir(os.path.join(mia_path, 'populse_mia')):
        #     message = ('A "populse_mia" folder already exists in the selected '
        #                'path for the populse_mia install')
        #     self.msg = QtWidgets.QMessageBox()
        #     self.msg.setIcon(QtWidgets.QMessageBox.Warning)
        #     self.msg.setText(message)
        #     self.msg.setInformativeText('By pressing "OK", this folder and its '
        #                                 'content will be removed.')
        #     self.msg.setWindowTitle("Warning")
        #     self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok |
        #                                 QtWidgets.QMessageBox.Cancel)
        #     self.msg.buttonClicked.connect(self.ok_or_abort)
        #     self.msg.exec()

        # If the user has clicked on "Cancel" the installation is aborted
        # if self.folder_exists_flag:
        #     return
        #
        # else:
        #     shutil.rmtree(os.path.join(mia_path, 'populse_mia'),
        #                   ignore_errors=True)

        # MRIFileManager folder management / initialisation:
        mri_conv_dir = os.path.join(properties_path, 'mri_conv')

        if os.path.isdir(mri_conv_dir):
            message = ("A 'mri_conv' folder already exists in the {} "
                       "folder!".format(properties_path))
            self.msg = QtWidgets.QMessageBox()
            self.msg.setIcon(QtWidgets.QMessageBox.Warning)
            self.msg.setText(message)
            self.msg.setInformativeText("Hit 'OK' to overwrite this folder "
                                        "and its contents.\nPressing 'Cancel' "
                                        "will abort the installation.")
            self.msg.setWindowTitle("Warning")
            self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok |
                                        QtWidgets.QMessageBox.Cancel)
            self.msg.buttonClicked.connect(self.ok_or_abort)
            self.msg.exec()

        # If the user has clicked on "Cancel" the installation is aborted
        if self.folder_exists_flag:
            return

        else:
            shutil.rmtree(mri_conv_dir, ignore_errors=True)



        self.properties_dir = os.path.abspath(properties_dir)
        self.projects_save_path = os.path.abspath(projects_path)
        self.mri_conv_path = os.path.abspath(mri_conv_dir)

        self.set_new_layout()

        # # Creating a "projects" folder in the specified projects folder
        # if not os.path.isdir(os.path.join(projects_path, 'projects')):
        #
        #     try:
        #         os.mkdir(os.path.join(projects_path, 'projects'))
        #
        #     except OSError as e:
        #         print('Error creating the "projects" folder: ', e)

        # Creates populse_mia folder to the specified location
        # populse_mia_folder = os.path.join(mia_path, 'populse_mia')
        # self.make_populse_mia_folder(populse_mia_folder)

        # Updating the checkbox
        self.check_box_mia.setChecked(True)
        QtWidgets.QApplication.processEvents()

        # # Moving MRIFileManager folder to the specified location
        # self.copy_directory('MRIFileManager',
        #                     os.path.join(mia_path, 'MRIFileManager'))

        self.make_mrifilemanager_folder(mri_conv_dir)

        # Clone MiaResources
        miaresources_dir = os.path.join(properties_path, 'miaresources')
        self.mia_resources_path = os.path.abspath(miaresources_dir)

        if os.path.isdir(miaresources_dir):
            message = ("A 'miaresources' folder already exists in the {} "
                       "folder!".format(properties_path))
            self.msg = QtWidgets.QMessageBox()
            self.msg.setIcon(QtWidgets.QMessageBox.Warning)
            self.msg.setText(message)
            self.msg.setInformativeText("Hit 'OK' to overwrite this folder "
                                        "and its contents.\nPressing 'Cancel' "
                                        "will abort the installation.")
            self.msg.setWindowTitle("Warning")
            self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok |
                                        QtWidgets.QMessageBox.Cancel)
            self.msg.buttonClicked.connect(self.ok_or_abort)
            self.msg.exec()

        # If the user has clicked on "Cancel" the installation is aborted
        if self.folder_exists_flag:
            return

        else:
            shutil.rmtree(miaresources_dir, ignore_errors=True)

        self.clone_miaResources(miaresources_dir)

        # Updating the checkbox
        self.check_box_mri_conv.setChecked(True)
        QtWidgets.QApplication.processEvents()

        # Adding both mia, MRIFileManager and projects paths to
        # populse_mia's config
        # config_file = os.path.join(mia_path,
        #                            'populse_mia',
        #                            'properties',
        #                            'config.yml')
        # if os.path.isfile(config_file):
        #     config_dic = self.load_config(config_file)
        #     config_dic["projects_save_path"] = os.path.join(projects_path,
        #                                                     'projects')
        #     config_dic["resources_path"] = os.path.join(mia_path,
        #                                                 'MiaResources')
        #     config_dic["mri_conv_path"] = os.path.join(mia_path,
        #                                                'MRIFileManager',
        #                                                'MRIManager.jar')
        #     config_dic["clinical_mode"] = use_clinical_mode
        #     config_dic["use_matlab"] = use_matlab
        #     config_dic["matlab"] = matlab
        #     config_dic["matlab_standalone"] = matlab_standalone
        #     config_dic["use_spm"] = use_spm
        #     config_dic["spm"] = spm
        #     config_dic["use_spm_standalone"] = use_spm_standalone
        #     config_dic["spm_standalone"] = spm_standalone
        #     self.save_config(config_dic, config_file, fernet=True)
        #
        # else:
        #     print('\nWarning! No {} file found ...\n'.format(config_file))


        # Adding properties_user_path to dot_mia_config file
        mia_home_properties_path_new["properties_user_path"] = os.path.dirname(properties_path)


        mia_home_properties_path = {
                **mia_home_properties_path,
                **mia_home_properties_path_new,
            }
        with open(dot_mia_config,
                  "w",
                  encoding="utf8") as configfile:
            yaml.dump(
                mia_home_properties_path,
                configfile,
                default_flow_style=False,
                allow_unicode=True,
            )

        config = Config()
        config.set_projects_save_path(projects_path)
        config.set_resources_path(miaresources_dir)
        config.set_mri_conv_path(os.path.join(mri_conv_dir, 'MRIFileManager',
                                                'MRIManager.jar')
                                 )
        config.set_clinical_mode(use_clinical_mode)
        config.set_use_matlab(use_matlab)
        config.set_matlab_path(matlab)
        config.set_matlab_standalone_path(matlab_standalone)
        config.set_use_spm(use_spm)
        config.set_spm_path(spm)
        config.set_use_spm_standalone(use_spm_standalone)
        config.set_spm_standalone_path(spm_standalone)


        # self.save_config(home_config, os.path.join(dot_mia_path,
        #                                            'configuration.yml'))

        # Updating the checkbox
        self.check_box_config.setChecked(True)
        QtWidgets.QApplication.processEvents()

        # Upgrading soma-base, soma_worflow and capsul: we don't know if these
        # packages are uptodate
        if host_target_install:
            self.upgrade_soma_capsul()

        if not host_target_install:
            self.uninstall_package('populse-db')
            self.uninstall_package('capsul')
            self.uninstall_package('soma-base')
            self.uninstall_package('soma-workflow')

        # Updating the checkbox
        self.check_box_pkgs.setChecked(True)
        QtWidgets.QApplication.processEvents()

        # Displaying the result of the installation
        self.last_layout()

    def install_matlab_api(self):
        pass
        # TODO: find a way to get the admin rights
        """cur_dir = os.getcwd()
        try:
            if self.matlab_path:
                os.chdir(os.path.join(self.matlab_path, 'extern', 'engines', 'python'))
                subprocess.call([sys.executable, 'setup.py', 'install'])
                os.chdir(cur_dir)
        except:
            os.chdir(cur_dir)"""

    @staticmethod
    def install_package(package):
        subprocess.call([sys.executable, '-m', 'pip', 'install', '--user',
                         '--upgrade', package])

    def last_layout(self):
        """Changing the layout to a temporary widget.

        Final layout after Mia installation
        """
        QtWidgets.QWidget().setLayout(self.v_box_install_status)

        # Setting a new layout
        self.mia_installed_label = QtWidgets.QLabel("Mia has been correctly "
                                                    "installed.")
        self.mia_installed_label.setFont(self.top_label_font)

        h_box_top_label = QtWidgets.QHBoxLayout()
        h_box_top_label.addStretch(1)
        h_box_top_label.addWidget(self.mia_installed_label)
        h_box_top_label.addStretch(1)

        mia_label_text = "- Mia configuration path: {0}".format(self.properties_dir)
        projects_label_text = "- projects path: {0}".format(
            self.projects_save_path)
        mri_conv_label_text = "- MRIFileManager path: {0}".format(
            self.mri_conv_path)
        mia_resources_label_text = "- MiaResources path: {0}".format(
            self.mia_resources_path)
        operating_mode_label_text = ("Populse_MIA has been installed with {0} "
                                     "mode.").format(self.operating_mode)

        mia_label = QtWidgets.QLabel(mia_label_text)
        projects_label = QtWidgets.QLabel(projects_label_text)
        mri_conv_label = QtWidgets.QLabel(mri_conv_label_text)
        mia_resources_label = QtWidgets.QLabel(mia_resources_label_text)
        operating_mode_label = QtWidgets.QLabel(operating_mode_label_text)

        mia_command_label_text = ("To launch populse_mia, execute one of these "
                                  "command lines depending on your Python "
                                  "setup:\n\n"
                                  "python3 -m populse_mia\n\n"
                                  "python -m populse_mia")
        mia_command_label = QtWidgets.QLabel(mia_command_label_text)
        mia_command_label.setFont(self.top_label_font)

        button_quit = QtWidgets.QPushButton("Quit")
        button_quit.clicked.connect(self.close)

        h_box_button = QtWidgets.QHBoxLayout()
        h_box_button.addStretch(1)
        h_box_button.addWidget(button_quit)

        v_box_last_layout = QtWidgets.QVBoxLayout()
        v_box_last_layout.addLayout(h_box_top_label)
        v_box_last_layout.addStretch(1)
        v_box_last_layout.addWidget(mia_label)
        v_box_last_layout.addWidget(projects_label)
        v_box_last_layout.addWidget(mri_conv_label)
        v_box_last_layout.addWidget(mia_resources_label)
        v_box_last_layout.addStretch(1)
        v_box_last_layout.addWidget(operating_mode_label)
        v_box_last_layout.addStretch(1)
        v_box_last_layout.addWidget(mia_command_label)
        v_box_last_layout.addStretch(1)
        v_box_last_layout.addLayout(h_box_button)

        self.setLayout(v_box_last_layout)

        QtWidgets.QApplication.processEvents()

    # @staticmethod
    # def load_config(config_file):
    #     f = Fernet(CONFIG)
    #
    #     with open(config_file, 'rb') as stream:
    #
    #         try:
    #             stream = b"".join(stream.readlines())
    #             decrypted = f.decrypt(stream)
    #
    #             if version.parse(yaml.__version__) > version.parse('5.1'):
    #                 return yaml.load(decrypted, Loader=yaml.FullLoader)
    #
    #             else:
    #                 return yaml.load(decrypted)
    #
    #         except yaml.YAMLError as exc:
    #             print('error loading YAML file: %s' % config_file)
    #             print(exc)
    #
    #         # in case of problem, return an empty config
    #     return {}

    def make_mrifilemanager_folder(self, mri_conv_dir):
        # temp_dir = tempfile.mkdtemp()
        try:
            subprocess.call(['git', 'clone',
                            'https://github.com/populse/mri_conv.git',
                            mri_conv_dir])

        except Exception as e:
            print('\n{}...'.format(e))
            return

        # try:
        #     shutil.copytree(os.path.join(temp_dir, 'mri_conv',
        #                                  'MRIFileManager'),
        #                     os.path.join(mia_path, 'MRIFileManager'))
        #
        #     # Directories are the same
        # except shutil.Error as e:
        #     print('Directory not copied. Error: %s' % e)
        #
        # # Any error saying that the directory doesn't exist
        # except OSError as e:
        #     print('Directory not copied. Error: %s' % e)
        #
        # shutil.rmtree(temp_dir, ignore_errors=True)

    def clone_miaResources(self, miaresources_dir):
#        temp_dir = tempfile.mkdtemp()
        try:
            subprocess.call(['git', 'clone',
                            'https://gricad-gitlab.univ-grenoble-alpes.fr/condamie/miaresources.git',
                            miaresources_dir])

        except Exception as e:
            print('\n{}...'.format(e))
            return


        # try:
        #     shutil.copytree(os.path.join(temp_dir, 'MiaResources'),
        #                     os.path.join(mia_path, 'MiaResources'))
        #
        # # Directories are the same
        # except shutil.Error as e:
        #     print('Directory not copied. Error: %s' % e)
        #
        # # Any error saying that the directory doesn't exist
        # except OSError as e:
        #     print('Directory not copied. Error: %s' % e)
        #
        # shutil.rmtree(temp_dir, ignore_errors=True)

    # def make_populse_mia_folder(self, populse_mia_folder):
    #     os.makedirs(os.path.join(populse_mia_folder, 'processes',
    #                              'User_processes'))
    #     Path(os.path.join(populse_mia_folder, 'processes',
    #                       'User_processes', '__init__.py')).touch()
    #
    #     os.makedirs(os.path.join(populse_mia_folder, 'properties'))
    #     saved_projects = {'paths': []}
    #     self.save_config(saved_projects,
    #                      os.path.join(populse_mia_folder, 'properties',
    #                                   'saved_projects.yml'),
    #                      fernet=False)
    #     self.save_config('gAAAAABd79UO5tVZSRNqnM5zzbl0KDd7Y98KCSKCNizp9aDqADs9'
    #                      'dAQHJFbmOEX2QL_jJUHOTBfFFqa3OdfwpNLbvWNU_rR0VuT1Zdlm'
    #                      'TYv4wwRjhlyPiir7afubLrLK4Jfk84OoOeVtR0a5a0k0WqPlZl-y'
    #                      '8_Wu4osHeQCfeWFKW5EWYF776rWgJZsjn3fxZ-V2g5aHo-Q5aqYi'
    #                      '2V1Kc-kQ9ZwjFBFbXNa1g9nHKZeyd3ve6p3RUSELfUmEhS0eOWn8'
    #                      'i-7GW1UGa4zEKCsoY6T19vrimiuRVy-DTmmgzbbjGkgmNxB5MvEz'
    #                      's0BF2bAcina_lKR-yeICuIqpTSOBfgkTDcB0LVPBoQmogUVVTeCr'
    #                      'jYH9_llFTJQ3ZtKZLdeStFR5Y2I2ZkQETi6m-0wmUDKf-KRzmk6s'
    #                      'LRK_oz6Gmu'
    #                      'TAN8A51au2v1M=', os.path.join(populse_mia_folder,
    #                                                     'properties',
    #                                                     'config.yml'),
    #                      fernet=False)

    def ok_or_abort(self, button):
        role = self.msg.buttonRole(button)

        if role == QtWidgets.QMessageBox.AcceptRole:  # "OK" has been clicked
            self.folder_exists_flag = False

        else:
            self.folder_exists_flag = True

    # @staticmethod
    # def save_config(config_dic, config_file, fernet=False):
    #     if fernet is True:
    #         f = Fernet(CONFIG)
    #         with open(config_file, 'wb') as configfile:
    #             stream = yaml.dump(config_dic, default_flow_style=False,
    #                                allow_unicode=True)
    #             configfile.write(f.encrypt(stream.encode()))
    #     else:
    #         with open(config_file, 'w', encoding='utf8') as configfile:
    #             yaml.dump(config_dic, configfile, default_flow_style=False,
    #                       allow_unicode=True)

    def set_new_layout(self):
        """Changing the layout to a temporary widget.

        Last step of the installation.
        """
        QtWidgets.QWidget().setLayout(self.global_layout)

        # Setting a new layout
        self.mia_installing_label = QtWidgets.QLabel("Mia is getting installed."
                                                     " Please wait! ...")
        self.mia_installing_label.setFont(self.top_label_font)

        h_box_top_label = QtWidgets.QHBoxLayout()
        h_box_top_label.addStretch(1)
        h_box_top_label.addWidget(self.mia_installing_label)
        h_box_top_label.addStretch(1)

        self.status_label = QtWidgets.QLabel("Status:")

        self.check_box_mia = QtWidgets.QCheckBox("Installing Mia")

        self.check_box_mri_conv = QtWidgets.QCheckBox("Installing "
                                                      "MRIFileManager")

        self.check_box_config = QtWidgets.QCheckBox("Writing config file")

        self.check_box_pkgs = QtWidgets.QCheckBox("Installing Python packages "
                                                  "(may take a few minutes)")

        self.v_box_install_status = QtWidgets.QVBoxLayout()
        self.v_box_install_status.addLayout(h_box_top_label)
        self.v_box_install_status.addWidget(self.status_label)
        self.v_box_install_status.addWidget(self.check_box_mia)
        self.v_box_install_status.addWidget(self.check_box_mri_conv)
        self.v_box_install_status.addWidget(self.check_box_config)
        self.v_box_install_status.addWidget(self.check_box_pkgs)
        self.v_box_install_status.addStretch(1)

        self.setLayout(self.v_box_install_status)

        QtWidgets.QApplication.processEvents()

    @staticmethod
    def uninstall_package(package):
        try:
            subprocess.call([sys.executable, '-m', 'pip', 'uninstall',
                             '--yes', package])

        except Exception:
            subprocess.call(['pip3', 'uninstall', '--yes', package])

    def upgrade_soma_capsul(self):
        temp_dir = tempfile.mkdtemp()
        cwd = os.getcwd()

        try:
            # Updating soma-base
            self.uninstall_package('soma-base')
            subprocess.call(['git', 'clone',
                             'https://github.com/populse/soma-base.git',
                             os.path.join(temp_dir, 'soma-base')])
            os.chdir(os.path.join(temp_dir, 'soma-base'))
            subprocess.call([sys.executable, 'setup.py', 'install', '--user',
                            '--force', '--prefix='])

        except:
            print('\n\nProblem while upgrading soma-base...')

            '''if not os.name == 'nt':  # if not on windows
                   self.uninstall_package('capsul')
                   os.chmod('upgrade_capsul.sh', 0o777)
                   subprocess.call('./upgrade_capsul.sh', shell=True)

                    self.uninstall_package('soma-base')
                    os.chmod('upgrade_soma.sh', 0o777)
                    subprocess.call('./upgrade_soma.sh', shell=True)
            '''

        try:
            # Updating soma-workflow
            self.uninstall_package('soma-workflow')
            subprocess.call(['git', 'clone',
                             'https://github.com/populse/soma-workflow.git',
                             os.path.join(temp_dir, 'soma-workflow')])
            os.chdir(os.path.join(temp_dir, 'soma-workflow'))
            subprocess.call([sys.executable, 'setup.py', 'install', '--user',
                            '--force', '--prefix='])

        except:
            print('\n\nProblem while upgrading soma-workflow...')

        try:
            # Updating capsul
            self.uninstall_package('capsul')
            subprocess.call(['git', 'clone',
                             'https://github.com/populse/capsul.git',
                             os.path.join(temp_dir, 'capsul')])
            os.chdir(os.path.join(temp_dir, 'capsul'))
            subprocess.call([sys.executable, 'setup.py', 'install', '--user',
                             '--force', '--prefix='])

        except:
            print('\n\nProblem while upgrading capsul...')

        os.chdir(cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def use_matlab_changed(self):
        """
        Called when the use_matlab checkbox is changed
        """

        if not self.use_matlab_checkbox.isChecked():
            self.matlab_choice.setDisabled(True)
            self.matlab_standalone_choice.setDisabled(True)
            self.spm_choice.setDisabled(True)
            self.spm_standalone_choice.setDisabled(True)
            self.matlab_label.setDisabled(True)
            self.matlab_standalone_label.setDisabled(True)
            self.spm_label.setDisabled(True)
            self.spm_standalone_label.setDisabled(True)
            self.spm_browse.setDisabled(True)
            self.spm_standalone_browse.setDisabled(True)
            self.matlab_browse.setDisabled(True)
            self.matlab_standalone_browse.setDisabled(True)
            self.use_spm_checkbox.setChecked(False)
            self.use_spm_standalone_checkbox.setChecked(False)
        else:
            self.matlab_choice.setDisabled(False)
            self.matlab_standalone_choice.setDisabled(False)
            self.matlab_label.setDisabled(False)
            self.matlab_standalone_label.setDisabled(False)
            self.matlab_browse.setDisabled(False)
            self.matlab_standalone_browse.setDisabled(False)

    def use_spm_changed(self):
        """
        Called when the use_spm checkbox is changed
        """

        if not self.use_spm_checkbox.isChecked():
            self.spm_choice.setDisabled(True)
            self.spm_label.setDisabled(True)
            self.spm_browse.setDisabled(True)
        else:
            self.spm_choice.setDisabled(False)
            self.spm_label.setDisabled(False)
            self.spm_browse.setDisabled(False)
            self.spm_standalone_choice.setDisabled(True)
            self.spm_standalone_label.setDisabled(True)
            self.spm_standalone_browse.setDisabled(True)
            self.use_spm_standalone_checkbox.setChecked(False)

    def use_spm_standalone_changed(self):
        """
        Called when the use_spm_standalone checkbox is changed
        """

        if not self.use_spm_standalone_checkbox.isChecked():
            self.spm_standalone_choice.setDisabled(True)
            self.spm_standalone_label.setDisabled(True)
            self.spm_standalone_browse.setDisabled(True)
        else:
            self.spm_standalone_choice.setDisabled(False)
            self.spm_standalone_label.setDisabled(False)
            self.spm_standalone_browse.setDisabled(False)
            self.spm_choice.setDisabled(True)
            self.spm_label.setDisabled(True)
            self.spm_browse.setDisabled(True)
            self.use_spm_checkbox.setChecked(False)
