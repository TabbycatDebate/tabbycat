.. _install-local:

===================
Local Installations
===================

What is a local installation?
=============================

Tabbycat is a web-based system: it's designed to run as a web site. However, instead of installing it on a web server, you can install it on your computer, serving web pages to yourself. This is called a local installation.

Then, when you open your browser, you can use Tabbycat like any other web site. The only difference is that this one is on **your** computer, not some computer in a data centre in a far-away land. In effect, you are getting your computer to behave like a web server.

.. _install-decision:

Should I use a local installation?
==================================

In most cases, you should make an online Tabbycat installation by :ref:`setting up an instance on Heroku <install-heroku>`. This has a number of major advantages:

- The installation process is easier.
- You can enter ballots and manage your tournament from multiple computers.
- Participants can access the draw, motions, results and more online.
- Heroku's data centers are less likely to fail than your computer is.
- Heroku e-mails Tabbycat's developers error reports to help us fix bugs.

In some cases, you might have a good reason to use a local installation. We can
think of just one such reason: If you won't have access to the internet at your
tournament, or if internet access will be flaky, then you should use a local
installation.

.. attention:: You'll need internet access to download dependencies during the
  local installation process. So if you're not expecting to have reliable
  internet access at your tournament, be sure to have Tabbycat installed
  *before* you get there!

.. admonition:: Advanced users
  :class: tip

  Tabbycat is a `Django <https://www.djangoproject.com/>`_ project, so if you
  have your own preferred method of running Django projects, you can also do
  that. Just be aware that we haven't tried it.

Okay, so how do I do it?
========================

The easiest option is to :ref:`install Tabbycat using Docker <install-docker>`. This method should work across all operating systems and is by far the easiest way to get a local copy running.

If installing using Docker does not work, or if you want to be able to modify Tabbycat's code we also have a number of instructions for manually setting up a copy of Tabbycat. There instructions are here:

- :ref:`install-linux`
- :ref:`install-osx`
- :ref:`install-wsl`
- :ref:`install-windows`

Advanced uses
=============

Can others access my local install?
-----------------------------------

Local installations can also take advantage of multiple-computer site access, including data entry---it's just takes more work than a Heroku installation to set up.

Since a local installation is just having your computer run a web server, it can serve other computers too. You can make this work even if you don't have internet access: all you need is a router that you can use to connect a few computers together. Then other computers on your local network can access the Tabbycat site hosted on your computer. We did this at Victoria Australs 2012.

We don't provide detailed instructions for this; we leave it for advanced users to set up themselves. As a rough guide:

- You need to pass in your computer's IP address and port to the `runserver` command, for example, if your computer (the one acting as a server) is 196.168.0.2 and you want to run it on port 8000: ``dj runserver 192.168.0.2:8000``
- You need to configure your firewall settings to allow incoming connections on the IP address and port you specified in that command.
- Be aware that local installs use the Django development server, whose **security is not tested**. Therefore, it's a good idea to make sure your firewall **only lets in computers on your local network** (or, if you're really paranoid, isolate the network from the internet completely).

Can I run an internet-accessible website from a local installation?
-------------------------------------------------------------------

Probably not. Even if you disable your firewall, chances are your home router (or university router) will block any connections from the outside world to you. Even if you can though, **you really shouldn't**. The local installation uses the *Django development server*, which is a lightweight server designed for developers. Specifically, Django **does not test the security of its development server** in the way that proper web servers do. That is: It's a security risk to run a local installation as an internet-accessible site. Don't do it. `Install Tabbycat on Heroku <install-heroku>`_ instead.

Alternatively, if you have a background in web development, you might choose to install Tabbycat on your own production server. It's a Django project, so any means of supporting Django projects should work fine.

It's safe to run on a small, isolated network (see above) with your firewall correctly configured because you presumably trust everyone you let on the network!
