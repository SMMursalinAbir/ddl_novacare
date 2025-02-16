from odoo import models, api
import subprocess
import sys
import os


class Packages:
    """
    This Class installs required Packages or library
    """
    get_pckg = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    installed_packages = [r.decode().split('==')[0] for r in get_pckg.split()]
    # List of your required packages
    required_packages = ['geocoder']
    for packg in required_packages:
        if packg in installed_packages:
            pass
        else:
            print('installing package %s' % packg)
            os.system('pip3 install ' + packg)