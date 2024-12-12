#!/usr/bin/env python

import sys
import os
import glob
import yaml
import shutil
import subprocess
import pkgutil
from collections import namedtuple

from setuptools import setup, find_namespace_packages, Command as _Command
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
from setuptools.dist import Distribution

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


# !!! DO NOT REMOVE THIS !!! #
version_info = namedtuple('version_info', ['major', 'minor', 'patch'])
version_info.__new__.__defaults__ = (1, 4, 0)
version_info.__repr__ = lambda self: ".".join(map(str, self))
version_info.__str__ = lambda self: ".".join(map(str, self))
# !!! DO NOT REMOVE THIS !!! #

# !!! Modifying any of the constants below may break uip-cli support !!! #
EXTENSION_SRC_DIR = 'src'
BIN_FOLDER = 'bin'
EXTENSION_YML_PATH = os.path.join(EXTENSION_SRC_DIR, 'extension.yml')
THIRD_PARTY_SRC_DIR = '3pp'
THIRD_PARTY_PACKAGE = THIRD_PARTY_SRC_DIR.split('/')[-1]
THIRD_PARTY_BIN_FOLDER = os.path.join(THIRD_PARTY_SRC_DIR, BIN_FOLDER)
REQUIREMENTS_TXT = 'requirements.txt'
DEP_WHEEL_DIR = os.path.join('dist', 'dep')


class InstallDependencies(_Command):
    """Installs any Python packages specified in 'REQUIREMENTS_TXT' to the
    'THIRD_PARTY_SRC_DIR' folder

    Usage
    -----
    >>> python setup.py install_deps
    >>> python setup.py install_deps --reinstall-deps

    Parameters
    ----------
    _Command : setuptools.Command
    """

    # Set class attributes
    user_options = [
        ('reinstall-deps', 'f', 'deletes {0} folder and reinstalls any modules '\
         'specified in {1}'.format(THIRD_PARTY_SRC_DIR, REQUIREMENTS_TXT))
    ]
    boolean_options = ['reinstall-deps']
    description = "install dependencies specified in {0} to {1}".format(
        REQUIREMENTS_TXT, THIRD_PARTY_SRC_DIR)

    def initialize_options(self):
        self.reinstall_deps = False

    def finalize_options(self):
        if self.reinstall_deps is None:
            self.reinstall_deps = False

    def run(self):
        # If 'REQUIREMENTS_TXT' exists in the current folder, then install all
        # dependencies to 'THIRD_PARTY_SRC_DIR'
        if self.reinstall_deps and os.path.exists(THIRD_PARTY_SRC_DIR):
            print("Deleting '{}'".format(THIRD_PARTY_SRC_DIR))
            shutil.rmtree(THIRD_PARTY_SRC_DIR)
        if os.path.exists(REQUIREMENTS_TXT):
            print("Installing dependencies in '{}'".format(THIRD_PARTY_SRC_DIR))
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r',
                                   REQUIREMENTS_TXT, '-t', THIRD_PARTY_SRC_DIR,
                                   '--no-compile'])
        else:
            print("Nothing to do ({} not found)".format(REQUIREMENTS_TXT))


class BuildDependencyWheel(_bdist_wheel, _Command):
    """Builds a platform-specific wheel file containing all the packages in
    'THIRD_PARTY_SRC_DIR'

    Usage
    -----
    # Successful: assuming 'zip_safe' in 'extension.yml' is set to False
    >>> python setup.py bdist_dep_whl

    # Failure: assuming 'zip_safe' in 'extension.yml' is set to True
    >>> python setup.py bdist_dep_whl


    Parameters
    ----------
    _bdist_wheel : wheel.bdist_wheel.bdist_wheel
    """

    # Set class attributes
    description = "builds the dependency wheel file containing packages from {}".format(
        THIRD_PARTY_SRC_DIR)

    def __init__(self, dist):
        super().__init__(dist)

    def initialize_options(self):
        super().initialize_options()

        # Must override the class to force wheel to generate correct package name
        class ExtModules(list):
            def __bool__(self):
                return True

        # The distribution name, version, description etc. is automatically
        # populated by the call to the 'setup' function below. The rest of the
        # attributes are set accordingly.
        self.distribution.package_dir = {'': THIRD_PARTY_SRC_DIR}
        packages = find_namespace_packages(where=THIRD_PARTY_SRC_DIR)
        if os.path.exists(THIRD_PARTY_BIN_FOLDER):
            # Must include the 'bin' folder in the list of packages to build.
            packages.append(BIN_FOLDER)
        self.distribution.packages = packages
        self.distribution.include_package_data = True
        # Needed to grab all the '*.so'/'*.pyd' files
        self.distribution.package_data = {'': ['*']}
        # Needed to ensure wheel generates the correct package name
        self.distribution.ext_modules = ExtModules()
        self.distribution.has_ext_modules = lambda: True

        # Package all single file Python modules (e.g. six.py)
        self.distribution.py_modules = []
        for _, module_name, is_pkg in pkgutil.iter_modules([THIRD_PARTY_SRC_DIR]):
            if is_pkg:
                # All packages are already included by the `find_namespace_packages`
                # call above
                continue

            self.distribution.py_modules.append(module_name)

        # Get a list of any additional files in the '3pp' folder that need to
        # be packaged. This includes all files except single file Python
        # modules, which are included by `py_modules` above.
        data_files = []
        for f in os.listdir(THIRD_PARTY_SRC_DIR):
            full_path = os.path.join(THIRD_PARTY_SRC_DIR, f)

            if not os.path.isfile(full_path) or full_path.endswith(".py"):
                continue

            data_files.append(full_path)

        # Package the data files in the root of the wheel file. Without the
        # 'os.path.normpath("../../")', they would be placed in a '.data'
        # folder (which is not the desired location).
        if data_files:
            self.distribution.data_files = [
                (os.path.normpath("../../"), data_files)
            ]
        else:
            self.distribution.data_files = []

        self.dist_dir = DEP_WHEEL_DIR

    def finalize_options(self):
        return super().finalize_options()

    def run(self):
        if not os.path.exists(THIRD_PARTY_SRC_DIR):
            print('Nothing to do ({} folder does not exist)'.format(
                THIRD_PARTY_SRC_DIR))
            return

        super().run()


class build_py(_build_py):
    """Override setuptools's build_py class to implement additional
    logic to support extension packaging.
    """

    def get_module_outfile(self, build_dir, package, module):
        """Third party folder normally contains packages but it
        can also contains standalone modules such as six.py,
        for these modules we will move it to the root of the
        zip file to maintain consistency.
        """
        if package == [THIRD_PARTY_PACKAGE]:
            outfile_path = [build_dir] + [module + ".py"]
        else:
            outfile_path = [build_dir] + list(package) + [module + ".py"]

        return os.path.join(*outfile_path)


class bdist_egg(_bdist_egg, object):
    """Override setuptools's bdist_egg class to implement additional
    logic to support extension packaging.
    """

    def finalize_options(self):
        """Rename .egg extension to .zip"""
        super(bdist_egg, self).finalize_options()
        self.egg_output = '.'.join(
            [os.path.splitext(self.egg_output)[0], 'zip'])


def find_modules(where, package=None):
    """Find and return list of Python modules.

    Args:
        where (str): path to search for module files
        package (str): if specified, this will append to the modules name
                       in the output list
    Returns:
        Return list of modules, empty list is return if no modules
        is found under the search path
    """
    module_files = []

    for file in glob.glob(os.path.join(where, "*.py")):
        module = os.path.splitext(os.path.basename(file))[0]

        if package is None:
            module_files.append(module)
        else:
            module_files.append('.'.join([package, module]))

    return module_files


def get_package_dir(include_third_party_pkgs=True):
    """Return dict object contains full list of packages to be packaged"""
    # pacakge: dir, package is separated by . and dir is separated by /
    package_dir = {'': EXTENSION_SRC_DIR}

    if include_third_party_pkgs:
        package_dir.update({THIRD_PARTY_PACKAGE: THIRD_PARTY_SRC_DIR})
        # distutil convert_path automatically convert / to native os path separator
        # so just use / here regardless of os.sep
        package_dir.update({package: '{}/{}'.format(THIRD_PARTY_SRC_DIR,
                                                    package.replace('.', '/'))
                            for package in find_namespace_packages(THIRD_PARTY_SRC_DIR)})

    return package_dir


def get_wheel_dist_name(name, version):
    dist = Distribution(attrs={'name': name, 'version': version})
    bdist_wheel_cmd = dist.get_command_obj('bdist_wheel')
    bdist_wheel_cmd.ensure_finalized()

    return bdist_wheel_cmd.wheel_dist_name + '-'


def main():
    """Calls the setup() function from setuptools to generate an Extension
    package.

    Raises
    ------
    ValueError
        if 'zip_safe' is specified for API level other than 1.4.0 and above
    """
    # load meta data
    with open(EXTENSION_YML_PATH, 'r') as file:
        meta = yaml.load(file, Loader=Loader)

    # Extract the api level and parse it
    api_level = meta['extension']['api_level']
    major, minor, patch = [int(v) for v in api_level.split('.')]

    # Verify 'zip_safe' option is only specified for API level >=1.4.0
    if 'zip_safe' in meta['extension'] and major <= 1 and minor < 4:
        raise ValueError(
            "'zip_safe' is only valid for API level 1.4.0 and above")

    # Get the 'zip_safe' value, if specified or set to its default of True
    zip_safe = meta['extension'].get('zip_safe', True)

    setup_args = {
        'name': meta['extension']['name'],
        'version': meta['extension']['version'],
        'description': meta.get('extension', {}).get('description', ''),
        'author': meta.get('owner', {}).get('name', ''),
        'author_email': meta.get('owner', {}).get('email', ''),
        'url': "https://stonebranch.com",
        'license': "Copyright 2023, Stonebranch Inc, All Rights Reserved.",
        'include_package_data': True
    }

    if not zip_safe:
        # Only package the wheel files that match extension name and version
        expected_wheel_name_and_version = get_wheel_dist_name(
            meta["extension"]["name"],
            meta["extension"]["version"]
        )

        dep_wheel_files = []
        for wheel_file_path in glob.glob("{}/*.whl".format(DEP_WHEEL_DIR)):
            wheel_file_name = os.path.basename(wheel_file_path)
            if wheel_file_name.startswith(expected_wheel_name_and_version):
                dep_wheel_files.append(wheel_file_path)

        setup_args.update({
            'zip_safe': False,
            'package_dir': get_package_dir(include_third_party_pkgs=False),
            'packages': find_namespace_packages(EXTENSION_SRC_DIR),
            'py_modules': find_modules(EXTENSION_SRC_DIR),
            'data_files': [('', [EXTENSION_YML_PATH]), (os.path.basename(
                DEP_WHEEL_DIR), dep_wheel_files)],
            'cmdclass': {'build_py': build_py, 'bdist_egg': bdist_egg,
                         'install_deps': InstallDependencies,
                         'bdist_dep_whl': BuildDependencyWheel}
        })
    else:
        setup_args.update({
            'zip_safe': True,
            'package_data': {package: ['*']
                             for package in find_namespace_packages(THIRD_PARTY_SRC_DIR)},
            'package_dir': get_package_dir(),
            'packages': find_namespace_packages(THIRD_PARTY_SRC_DIR)
            + find_namespace_packages(EXTENSION_SRC_DIR),
            'py_modules': find_modules(EXTENSION_SRC_DIR)
            + find_modules(THIRD_PARTY_SRC_DIR, THIRD_PARTY_PACKAGE),
            'data_files': [('', [EXTENSION_YML_PATH]),
                           (BIN_FOLDER,
                            glob.glob('{}/**'.format(THIRD_PARTY_BIN_FOLDER)))],
            'cmdclass': {'build_py': build_py, 'bdist_egg': bdist_egg,
                         'install_deps': InstallDependencies}
        })

    setup(**setup_args)


if __name__ == '__main__':
    """
    Script Usage
    ------------
    # To install all third-party dependencies (assuming requirements.txt exists)
    >>> python setup.py clean --all install_deps

    # To reinstall all third-party dependencies (assuming requirements.txt exists)
    >>> python setup.py clean --all install_deps --reinstall-deps

    # To generate dependency wheel file (assuming zip_safe is False)
    >>> python setup.py clean --all bdist_dep_whl

    # To generate the extension archive
    >>> python setup.py clean --all bdist_egg
    """
    main()
