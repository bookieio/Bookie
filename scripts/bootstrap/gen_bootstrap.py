"""This will combine the custom additions with the original virtualenv script

A new bootstrap.py file will be generated for use

"""
import os
import textwrap
import virtualenv

bootstrap_file_path = os.path.dirname(__file__)
bootstrap_file = open(os.path.join(bootstrap_file_path, 'custom_bootstrap.py'))

output = virtualenv.create_bootstrap_script(textwrap.dedent(bootstrap_file.read()))
print output
