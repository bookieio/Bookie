======================
Setting Up Email Server
======================
For setting up a email server, please follow the instructions given below.

This assumes that you're on Ubuntu or can figure out the difference between
Ubuntu and your distro for the following:

::

    $ sudo apt-get install msmtp
    $ touch ~/.msmtprc
    $ chmod 0600 ~/.msmtprc


Now, you can edit the  *~/.msmtprc* file with your favourite text editor.
The configuration file should contain the following lines.

::

    defaults
    account examplemail
    host smtp.examplemail.com
    tls on
    tls_certcheck off
    port 587
    auth login
    from somebody@example.com
    user somebody@example.com
    password somesecret

    account default: examplemail


In the above example, the *host* has to be replaced with your email
service smtp host. The *from* and *user* has to be replaced with your email
address and *password* has to be replaced with your password.

Now, you can do a simple test to ensure your configuration is correct.
Copy and paste these lines to your command prompt modifying
the email address to your own address:

::

    cat <<EOF | msmtp someone@example.com
    Subject: test

    This is a test!
    EOF


If all the instructions are followed correctly, you can now receive the
activation mail to the specified email address.
