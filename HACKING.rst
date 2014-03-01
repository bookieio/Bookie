Typical Github workflow
=======================

Git allows you to work in a lot of different work flows. Here is one that
works well for our environment, if you are not already familiar with git.

To set up the environment, first fork the repository. Once the fork is
complete, create a local copy and work on a feature branch.

::

  git clone git@github.com:{yourusername}/Bookie.git
  cd Bookie
  # Add a second remote to the upstream Bookie repository your fork came from.
  # This lets you use commands such as `git pull bookieio develop` to update a
  # branch from the original trunk, as you'll see below.
  git remote add bookie git@github.com:bookieio/Bookie.git
  # Create a feature branch to work on.
  git checkout -b {featureBranchName}
  # Hacky hacky hacky


To push code for review, cleanup the commit history.

::

  # Optional: rebase your commit history into one or more meaningful commits.
  git rebase -i --autosquash
  # And push your feature branch up to your fork on Github.
  git push origin {featureBranchName}


In order to submit your code for review, you need to generate a pull request.
Go to your Github repository and generate a pull request to the `bookie:develop`
branch.

After review has been signed off on and the test run has updated the pull
request, a member of the `Bookieio` organization can submit the branch for landing.

Once the code has been landed you can remove your feature branch from both the
remote and your local fork. Github provides a button to do so in the bottom of
the pull request, or you can use git to remove the branch. Removing from your
local fork is listed below.

::

  git push origin :{featureBranchName}
  # And to remove your local branch
  git branch -D {featureBranchName}

Before creating another feature branch, make sure you update your fork's code
by pulling from the original Bookieio repository.

::

  # Using the alias from the Helpful aliases section, update your fork with
  # the latest code in the Bookie develop branch.
  git sync-bookie

  # And start your second feature branch.
  git checkout -b {featureBranch2}


Syncing your feature branch with develop (trunk)
-------------------------------------------------

Time to time you have a feature branch you've been working on for several days
while other branches have landed in trunk. To make sure you resolve any
conflicts before submitting your branch, it's often wise to sync your feature
branch with the latest from develop. You can do this by rebasing your branch
with develop.

The recommended pattern would be to

::

  # Update your local copy of develop with the latest from the bookie branch.
  git sync-bookie

  # Then check back out your feature branch and sync it with your new local
  # develop.
  git checkout {featureBranch}
  git sync-trunk

You should see messages for each landed branch getting rebased into your work.

::

    First, rewinding head to replay your work on top of it...
    Applying: Created local charm new or upgrade inspector.
    Applying: Refactored local charm upload helpers to support multiple service upgrades


Helpful Git tools and aliases
=============================

Tools
-----

`Git Remote Branch
<https://github.com/webmat/git_remote_branch>`_ - A tool to simplify working
with remote branches (Detailed installation instructions are in their readme).

Aliases
-------

Git provides a mechanism for creating aliases for complex or multi-step
commands. These are located in your ``.gitconfig`` file under the
``[alias]`` section.

If you would like more details on Git aliases, You can find out more
information here: `How to add Git aliases
<https://git.wiki.kernel.org/index.php/Aliases>`_

Below are a few helpful aliases we'll refer to in other parts of the
documentation to make working with the Bookie easier.

::

  ###
  ### QA a pull request branch on a remote e.g. Bookieio
  ###

  # Bring down the pull request number from the remote specified.
  # Note, the remote that the pull request is merging into may not be your
  # origin (your github fork).
  fetch-pr = "!f() { git fetch $1 +refs/pull/$2/head:refs/remotes/pr/$2; }; f"

  # Make a branch that merges a pull request into the most recent version of the
  # trunk (the "Bookieio" remote's develop branch). To do this, it also updates your
  # local develop branch with the newest code from trunk.
  # In the example below, "bookie" is the name of your remote, "6" is the pull
  # request number, and "qa-sticky-headers" is whatever branch name you want
  # for the pull request.
  # git qa-pr bookie 6 qa-adding-some-tests
  qa-pr = "!sh -c 'git checkout develop; git pull $0 develop; git checkout -b $2; git fetch-pr $0 $1; git merge pr/$1'"

  # Update your local develop branch with the latest from the bookie remote.
  # Then make sure to push that back up to your fork on github to keep
  # everything in sync.
  sync-bookie = "!f() { git checkout develop && git pull bookie develop && git push origin develop; }; f"

  # Rebase develop (trunk) into the current feature branch.
  sync-trunk = rebase develop

