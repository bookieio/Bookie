from fabric.api import env, local

# UNIT TESTING
def test():
    "Run the test suite locally. Much faster local vs run so separate function"
    local('nosetests {project_name}/tests'.format(**env), capture=False)
