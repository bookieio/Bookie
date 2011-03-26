"""These functions are added into a base virtualenv script

This lets us perform custom actions to make install/setup a one step process

"""
import os
import subprocess


try:
    import colorama as col
    COLOR = True

    # init the color output for terminals
    col.init()
except:
    print "CANNOT IMPORT colorama SO NO COLOR OUTPUT IS POSSIBLE"
    COLOR = False


def adjust_options(options, args):
    """Adjust the options set from the usage of the bootstrap.py script.

    We set no-site-packages to always be true

    """
    options.no_site_packages = True


def after_install(options, home_dir):
    """This is a hook to add this code to run after a new virtualenv"""

    class Out(object):
        """We wrap all output generators so we can colorize if we wish"""
        @staticmethod
        def line_break(type=None):
            length = 60
            print ""

            if not type:
                print '*' * length
            else:
                print type * length

        @staticmethod
        def error(output):
            """Specify a type of output to the user this is"""
            if COLOR:
                out = "{0}{1}ERROR: {2}{3}{4}{5}".format(col.Fore.WHITE,
                        col.Back.RED,
                        output,
                        col.Fore.RESET,
                        col.Back.RESET,
                        col.Style.RESET_ALL)
            else:
                out = "ERROR: " + output
            print out

        @staticmethod
        def warning(output):
            """Specify a type of output to the user this is"""
            if COLOR:
                out = "{0}{1}WARNING: {2}{3}{4}{5}".format(col.Fore.YELLOW,
                        col.Style.BRIGHT,
                        output,
                        col.Fore.RESET,
                        col.Back.RESET,
                        col.Style.RESET_ALL)
            else:
                out = "WARNING: " + output
            print out

        @staticmethod
        def success(output):
            """Specify a type of output to the user this is"""
            if COLOR:
                out = "{0}{1}{2}{3}{4}".format(col.Fore.GREEN,
                        output,
                        col.Fore.RESET,
                        col.Back.RESET,
                        col.Style.RESET_ALL)
            else:
                out = output
            print out

        @staticmethod
        def plain(output):
            """Just output the text plain to the terminal"""
            print output

    # define a ton of env vars we'll use in our scripted commands
    env = {}
    env['git_url'] = 'git://github.com/mitechie/Bookie.git'
    env['branch'] = 'feature/tools'

    # normalize this to the abs path so win/linux play nice
    # we have to do this retarded replacing of space with an escaped space so
    # that we don't get errors on directories with spaces in them.
    # we need to make this a raw string so spaces in the paths are ok
    env['home_dir'] = "{0!r}".format(os.path.abspath(home_dir))

    env['bin_path'] = os.path.abspath(os.path.join(home_dir, 'bin'))

    env['python_path'] = "{0!r}".format(os.path.join(env['bin_path'], 'python'))
    env['pip_path'] = "{0!r}".format(os.path.join(env['bin_path'], 'pip'))

    def _pip_require(req_src, **env):
        Out.line_break()
        Out.plain("Installing initial pip requirements from requirements.txt")

        cmd = [env['python_path'], env['pip_path'], 'install', '-q', '-E', env['home_dir'], '-r', req_src]

        print " ".join(cmd)
        subprocess.call(" ".join(cmd), shell=True)

    def install_app(**env):
        if env['branch'] != 'master':
            git_branch = '-b {branch}'.format(**env)
        else:
            git_branch = ''

        git_cmd = 'git clone {0} {git_url} {home_dir}{1}bookie'.format(git_branch, os.sep, **env)

        # there should be a checkout requirements.txt in that new git dir
        # the double dir names of bookie/Bookie are just known since they're
        # project directories
        req_path = env['home_dir']
        requirements_path = os.path.join(req_path.strip("'"), 'bookie',
                                         'Bookie', 'requirements.txt')

        subprocess.call(git_cmd, shell=True)

        if os.path.exists(requirements_path):
            _pip_require(requirements_path, **env)
        else:
            Out.error("No requirements.txt file located")

        # run setup.py on the project
        setup_path = os.path.join(env['home_dir'].strip("'"), 'bookie', 'Bookie')
        cmd = 'cd {0} && {python_path} setup.py develop'
        subprocess.call(cmd.format(setup_path, **env), shell=True)

        Out.line_break()
        Out.success("Your virtualenv is now ready to go")
        Out.warning("Please source {0}/bin/activate to activate the environment".format(home_dir))
        Out.plain("Continue to follow the app setup steps from the getting started guide - http://bmark.us/started.html")
        print ""


    # do the actual installation
    install_app(**env)

