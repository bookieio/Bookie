================================
bookie-manage admin script (CLI)
================================

*bookie-manage* is a tool to do some admin tasks.

::

    (Bookie)$ bookie-manage 
    usage: bookie-manage [-h] [--ini INI]  ...

    optional arguments:
      -h, --help      show this help message and exit
      --ini INI       The .ini configuration file to use for getting db access,
                      default is "bookie.ini"

    basic commands:
      
        list-user     Get the list of users
        new-user      Adding new user
        reset-password
                      Reset user password

    use "bookie-manage command --help" to see command parameters
    
By default, *bookie-manage* use ``bookie.ini`` configuration file.


Display user list
=================

::

    (Bookie)$ bookie-manage list-user
    +----------------+------+-----------------------------+
    | username       | name | email                       |
    +----------------+------+-----------------------------+
    | admin          | None | testing@dummy.com           |
    | stephane-klein | None | contact@stephane-klein.info |
    +----------------+------+-----------------------------+


Create a new user
=================

Create new user subcommand help :

::

    (Bookie)$ bookie-manage new-user --help
    usage: bookie-manage new-user [-h] [--username USERNAME] [--email EMAIL]
                                  [--password PASSWORD]

    optional arguments:
      -h, --help            show this help message and exit
      --username USERNAME, -u USERNAME
      --email EMAIL, -e EMAIL
      --password PASSWORD, -p PASSWORD


Create a new user :

::

    (Bookie)$ bookie-manage new-user --username stephane --email stephane@bmark.us --password secret
    New user created :
        username : stephane
        email : stephane@bmark.us
        password : secret


I can see new user in the list :

::

    (Bookie)$ bookie-manage list-user
    +----------------+------+-----------------------------+
    | username       | name | email                       |
    +----------------+------+-----------------------------+
    | admin          | None | testing@dummy.com           |
    | stephane-klein | None | contact@stephane-klein.info |
    | stephane       | None | stephane@bmark.us           |
    +----------------+------+-----------------------------+



Reset user password
===================

Reset password subcommand help :

::

    $ bookie-manage reset-password --help
    usage: bookie-manage reset-password [-h] [--username USERNAME]
                                        [--password PASSWORD]

    optional arguments:
      -h, --help            show this help message and exit
      --username USERNAME, -u USERNAME
      --password PASSWORD, -p PASSWORD

Reset ``stephane`` password :

::

    (Bookie)$ bookie-manage reset-password --username stephane --password newsecret
    Password updated
