import os
import subprocess
import urllib

try:
    import colorama as col
    COLOR = True

    # init the color output for terminals
    col.init()
except:
    print "CANNOT IMPORT colorama SO NO COLOR OUTPUT IS POSSIBLE"
    COLOR = False


def adjust_options(options, args):
    """Adjust the options set from the usage of the venv.py script.

    We set no-site-packages to always be true

    """
    options.no_site_packages = True

    if not options.install_type:
        options.install_type = 'package'


def extend_parser(optparse_parser):
    optparse_parser.add_option("-g", "--git", dest="git_repo",
                  help="specify existing git repository to install",
                  metavar="GIT_REPO")
    optparse_parser.add_option("-b", "--branch", dest="git_branch",
                  help="specify existing git branch or tag to switch to",
                  metavar="GIT_BRANCH")

    optparse_parser.add_option("-t", "--type", dest="install_type",
                  help=("Type of venv setup. Can be 'bare', 'package', 'pylons',"
                        " or 'quipp' currently."),
                  metavar="INSTALL_TYPE")

    optparse_parser.add_option("-n", "--pkg-name", dest="pkg_name",
                  help="Override the name of the package created with the -t package type",
                  metavar="PKG_NAME")

    optparse_parser.add_option("-i", "--indexes", dest="indexes",
                  help="Allow indexes with the pip install. Overrides the --no-index to pip",
                  metavar="INDEXES")


def after_install(options, home_dir):
    env = {}
    env['packagedir'] = 'http://sd2.morpace-i.com/packages/'
    env['git_url'] = 'gitosis@sd2.morpace-i.com:'

    env['fabfile_path'] = env['packagedir'] + 'fabfile.py'
    env['git_ignore_path'] = env['packagedir'] + '.gitignore'
    env['requirements_path'] = env['packagedir'] + 'requirements.txt'

    # normalize this to the abs path so win/linux play nice
    # we have to do this retarded replacing of space with an escaped space so
    # that we don't get errors on directories with spaces in them.
    env['home_dir'] = os.path.abspath(home_dir)

    env['bin_path'] = os.path.abspath(os.path.join(home_dir, 'bin'))

    env['python_path'] = "%r" % os.path.join(env['bin_path'], 'python')
    env['pip_path'] = "%r" % os.path.join(env['bin_path'], 'pip')
    env['paster_path'] = "%r" % os.path.join(env['bin_path'], 'paster')
    env['sphinx_start_path'] = "%r" % os.path.join(env['bin_path'], 'sphinx-quickstart')

    # we need to make this a raw string so spaces in the paths are ok
    env['home_dir'] = "%r" % os.path.abspath(home_dir)

    types = {}
    types['bare'] = {
        'docs_path': "{src_path}",
        'install_list': ['sphinx', 'nose', 'fabric', 'pep8'],
    }
    types['pylons'] = {
        'docs_path': "{src_path}",
        'install_list': ['pylons', 'sqlalchemy', 'MySQL-python', 'sphinx', 'nose', 'fabric', 'pep8'],
    }
    types['package'] = {
        'docs_path': "{src_path}",
        'install_list': ['sphinx', 'nose', 'fabric', 'pep8','modern-package-template'],
    }
    types['quipp'] = {
        'docs_path': "{src_path}",
        'install_list': ['quipp', 'pylons', 'sqlalchemy', 'MySQL-python',
                'sphinx', 'nose', 'fabric', 'pep8', 'morpylons',
                'sqlalchemy-migrate'],
    }


    def _line_break(type=None):
        length = 60
        print ""

        if not type:
            print '*' * length
        else:
            print type * length


    def _output_error(output):
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

    def _output_warning(output):
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

    def _output_success(output):
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

    def _output_plain(output):
        """Just output the text plain to the tmerinal"""
        print output

    def _docs_setup(docs_dir, **env):
        """Run the sphinx-quickstart for the new project"""
        _output_plain("Running docs setup")
        _output_warning("Make sure to keep the default docs path of '.'")

        if not os.path.exists(docs_dir):
            _output_plain('Creating docs path')
            os.makedirs(docs_dir)
        else:
            _output_warning("You already have a docs path")

        if not os.path.exists(os.path.join(docs_dir, 'index.rst')):
            cmd = ['cd', "%r" % docs_dir, '&&', env['python_path'], env['sphinx_start_path']]
            subprocess.call(" ".join(cmd), shell=True)
        else:
            _output_warning("You already seem to have an index.rst so not doing sphinx quickstart")


    def _pip_install(*args, **env):
        """Install a list of packages into the virtualenv"""
        for package in args:
            _output_plain("Installing: {0}".format(package))

            if allow_indexes:
                cmd = [env['python_path'], env['pip_path'], 'install', '-E', env['home_dir'],
                      '-f', env['packagedir'], package]
            else:
                cmd = [env['python_path'], env['pip_path'], 'install', '-E', env['home_dir'],
                      '--no-index', '-f', env['packagedir'], package]

            print " ".join(cmd)
            subprocess.call(" ".join(cmd), shell=True)

    def _pip_require(req_src, **env):
        _line_break()
        _output_plain("Installing initial pip requirements from requirements.txt")
        if allow_indexes:
            cmd = [env['python_path'], env['pip_path'], 'install', '-E', env['home_dir'], '-r', req_src]
        else:
            cmd = [env['python_path'], env['pip_path'], 'install', '-E', env['home_dir'], '--no-index', '-r', req_src]

        print " ".join(cmd)
        subprocess.call(" ".join(cmd), shell=True)

    def _pip_req_refresh(src_path, **env):
        """Recreate the requirements.txt file based on the virtualenv pkgs"""
        _output_plain("Generating fresh requirements.txt file from the current package selections")

        file_path = os.path.join(src_path, 'requirements.txt')

        # run pip freeze and nab the output of the command
        cmd = [env['python_path'], env['pip_path'], '-E', home_dir, 'freeze']
        pkg_list = subprocess.Popen(" ".join(cmd), stdout=subprocess.PIPE, shell=True).communicate()[0].strip()

        outfile = open(file_path, 'w')
        outfile.write("-f {0}\n".format(env['packagedir']))
        for l in pkg_list:
            outfile.write(l)

    def _install_samplefile(app_name, web_path, local_path, **env):
        """Download the sample file requested and put it in the new project

        """
        # we need to check that the local path does not exist already
        if os.path.exists(local_path):
            _output_warning("WARNING: Skipping installing file since it already exists - {0}".format(local_path))
            return
        else:
            _output_plain("Installing sample: {0}".format(web_path))
            fh = urllib.urlopen(web_path)
            oh = open(local_path, 'w')

            for l in fh:
                # replace the app
                l = l.replace('%(app_name)', app_name)
                l = l.replace('%(venv_path)', str(env['home_dir']).strip("'"))
                oh.write(l)

            fh.close()
            oh.close()


    def install_app(project_name, branch='master', **env):
        if project_name[-3:] == 'git':
            pass
        else:
            project_name = project_name + '.git'

        project_url = "{0}{1}".format(env['git_url'], project_name)
        app_name = os.path.basename(home_dir).rstrip('_ve') + '_app'
        checkout_path = "%r" % os.path.join(home_dir, app_name)

        if branch != 'master':
            git_branch = '-b {0}'.format(branch)
        else:
            git_branch = ''

        git_cmd = 'git clone {0} {1} {2}'.format(project_url, git_branch, checkout_path)

        # there should be a checkout requirements.txt in that new git dir
        req_path = checkout_path
        requirements_path = os.path.join(req_path.strip("'"), "requirements.txt")

        subprocess.call(git_cmd, shell=True)

        if os.path.exists(requirements_path):
            _pip_require(requirements_path, **env)
        else:
            _output_error("No requirements.txt file located")

        _line_break()
        _output_success("Your virtualenv is now ready to go")
        _output_warning("Please source {0}/bin/activate to activate the environment".format(home_dir))
        print ""
        _output_plain("You might need to now `python setup.py develop` the app")


    def setup_bare(alt_message=None, **env):
        # make the src directory for project use
        _line_break()
        _output_plain("Creating your src directory and installing initial deps")

        app_name = os.path.basename("%s" % env['home_dir']).strip("'").rstrip('_ve') + '_app'
        src_path = os.path.join(("%s" % env['home_dir']).strip("'"), app_name).strip("'")

        if os.path.exists(src_path):
            _output_warning("WARNING: Skipping creating src directory since it already exists")
        else:
            os.mkdir(src_path)

        # now make sure we install fabric
        _pip_install(*types['bare']['install_list'], **env)

        # and initial fabric file
        file_path = os.path.join(src_path, 'fabfile.py')
        _install_samplefile(app_name, env['fabfile_path'], file_path, **env)

        file_path = os.path.join(src_path, '.gitignore')
        _install_samplefile(app_name, env['git_ignore_path'], file_path, **env)

       # now generate a requirements.txt file based on the installed packages
        _pip_req_refresh(src_path, **env)

        docs_path = os.path.join(src_path, 'docs')
        _docs_setup(docs_path, **env)

        _line_break()
        _output_success("Your virtualenv is now ready to go")
        _output_warning("Please source {0}/bin/activate to activate the environment".format(home_dir)) 
        _output_warning("Make sure to update the fabfile.py as required for your app")
        print ""

    def setup_package(**env):
        """Create a new project with the modern-package-template tool

        """
        # make the src directory for project use
        _line_break()
        _output_plain("Creating your src directory and installing initial deps")

        app_name = os.path.basename(home_dir).rstrip('_ve')

        # now make sure we install packages
        _pip_install(*types['package']['install_list'], **env)

        if options.pkg_name:
            pkg_name = options.pkg_name
        else:
            pkg_name = app_name

        src_path = os.path.join(home_dir, pkg_name)

        # start the modern package template run
        if os.path.exists(src_path):
            _output_warning("Skipping creating src directory since it already exists")
        else:
            os.mkdir(src_path)
            package_cmd = ['cd', src_path, '&&', env['python_path'], env['paster_path'], 'create', '-t', 'modern_package', pkg_name]
            subprocess.call(" ".join(package_cmd), shell=True)

        # and initial fabric file
        file_path = os.path.join(src_path, 'fabfile.py')
        _install_samplefile(pkg_name, env['fabfile_path'], file_path, **env)

        file_path = os.path.join(src_path, '.gitignore')
        _install_samplefile(pkg_name, env['git_ignore_path'], file_path, **env)

        _pip_req_refresh(src_path, **env)

        docs_path = os.path.join(src_path, 'docs')
        _docs_setup(docs_path, **env)

        _line_break()
        _output_success("Your virtualenv is now ready to go")
        _output_warning("Please source {0}/bin/activate to activate the environment".format(home_dir))
        _output_warning("Make sure to update the fabfile.py as required for your app")
        print ""

    def setup_pylons(**env):
        # setup the pylons instance now
        pylons_app_name = os.path.basename(home_dir).rstrip('_ve') + '_app'

        app_path = os.path.join(("%s" % env['home_dir']).strip("'"), pylons_app_name)

        cd_cmd = "cd {0}".format(env['home_dir'])

        # now make sure we install packages
        _pip_install(*types['pylons']['install_list'], **env)

        # check that the pylons app does not already exist
        if os.path.exists(app_path):
            _output_warning("Skipping creating Pylons application since the directory already exists")
        else:
            pylons_cmd = [cd_cmd, "&&", env['python_path'], env['paster_path'],
                             'create', '-q', '--no-interactive', '-t', 'pylons', pylons_app_name,
                             'sqlalchemy=True template_engine=mako' ]

            os.popen(" ".join(pylons_cmd), 'w')

            docs_path = os.path.join(app_path, 'docs')
            _docs_setup(docs_path, **env)

            file_path = os.path.join(app_path, 'fabfile.py')
            _install_samplefile(pylons_app_name, env['fabfile_path'], file_path, **env)

            file_path = os.path.join(app_path, '.gitignore')
            _install_samplefile(pylons_app_name, env['git_ignore_path'], file_path, **env)

            _pip_req_refresh(app_path, **env)

            cd_cmd = "cd {0}".format("%r" % app_path)
            develop_cmd = cd_cmd + " && " + " ".join([env['python_path'], 'setup.py', 'develop'])
            os.popen(develop_cmd, 'w')

        _line_break()
        _output_success("Your pylons application {0} is now ready.".format(pylons_app_name))
        _output_warning("Please source {0}/bin/activate to activate the environment".format(home_dir))
        _output_plain("")
        _output_success("Then you can start the server with")
        _output_success("paster serve --reload {0}/{1}/development.ini".format(home_dir, pylons_app_name))

    def setup_quipp(**env):
        # setup the pylons instance now
        pylons_app_name = os.path.basename(home_dir).rstrip('_ve') + '_app'
        app_path = os.path.join(("%s" % env['home_dir']).strip("'"), pylons_app_name)

        cd_cmd = "cd {0}".format(env['home_dir'])

        # now make sure we install packages
        _pip_install(*types['quipp']['install_list'], **env)

        # check that the pylons app does not already exist
        if os.path.exists(app_path):
            _output_warning("Skipping creating Pylons application since the directory already exists")
        else:
            quipp_cmd = [cd_cmd, "&&", env['python_path'], env['paster_path'],
                             'create', '-t', 'quipp', pylons_app_name]

            subprocess.call(" ".join(quipp_cmd), shell=True)

            docs_path = os.path.join(app_path, 'docs')
            _docs_setup(docs_path, **env)

            file_path = os.path.join(app_path, 'fabfile.py')
            _install_samplefile(pylons_app_name, env['fabfile_path'], file_path, **env)

            file_path = os.path.join(app_path, '.gitignore')
            _install_samplefile(pylons_app_name, env['git_ignore_path'], file_path, **env)

            _pip_req_refresh(app_path, **env)

            cd_cmd = "cd {0}".format("%r" % app_path)
            develop_cmd = cd_cmd + " && " + " ".join([env['python_path'], 'setup.py', 'develop'])
            os.popen(develop_cmd, 'w')

        _line_break()
        _output_success("Your Quipp Portal {0} is now ready.".format(pylons_app_name))
        _output_warning("Please source {0}/bin/activate to activate the environment".format(home_dir))
        _output_plain("")
        _output_success("Then you can start the server with")
        _output_success("paster serve --reload {0}/{1}/development.ini".format(home_dir, pylons_app_name))
        _output_plain("")
        _line_break()
        _output_plain("For more details see the Quipp install docs at:")
        _output_plain("http://webint.morpace-i.com/sphinx/quipp/install.html")
        _output_plain("")

    if options.indexes and options.indexes.lower() == 'true':
        allow_indexes = True
    else:
        allow_indexes = False

    if options.git_repo:

        if options.git_branch:
            branch = options.git_branch
        else:
            branch = 'master'
        install_app(options.git_repo, branch=branch, **env)
    else:
        if options.install_type in types:
            # if the app is a pylons app run the pylons command
            if options.install_type == 'pylons':
                setup_pylons(**env)

            if options.install_type == 'quipp':
                setup_quipp(**env)


            if options.install_type == 'bare':
                setup_bare(**env)

            if options.install_type == 'package':
                setup_package(**env)

