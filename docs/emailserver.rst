=======================
Setting Up Email Server
=======================
To work with code in the signup process it's often best to setup email
communication for the site. It does not do this automatically and you need an
smtp server for it to send email out to test accounts.

One way to setup an smtp server is to use a small tool, msmtp.

This assumes that you're on Ubuntu. You'll need to adjust these instructions
for your own platform. If you get it working please feel free to submit a pull
request with your platform as we'll happily add it to the docs.

::

    $ sudo apt-get install msmtp
    $ touch ~/.msmtprc
    $ chmod 0600 ~/.msmtprc


Next, edit the  *~/.msmtprc* file with your favourite text editor.
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
service smtp host. The *from*, *user*, and *password*,  needs to be valid for
your own email account.

Once that's complete, you can perform simple test to ensure your configuration
is correct. Copy and paste these lines to your command prompt modifying the
email address to your own address:

::

    cat <<EOF | msmtp someone@example.com
    Subject: test

    This is a test!
    EOF


If all the instructions are followed correctly, you can now receive the
activation mail to the specified email address.
