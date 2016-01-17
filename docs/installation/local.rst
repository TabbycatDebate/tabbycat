.. _install-local:

===================
Local installations
===================

What is a local installation?
=============================

Tabbycat is a web-based system: it's designed to run as a web site. However, instead of installing it on a web server, you can install it on your computer, serving web pages to yourself. This is called a local installation.

Then, when you open your browser, you can use Tabbycat like any other web site. The only difference is that this one is on **your** computer, not some computer in a data centre in a far-away land.

In effect, you are getting your computer to behave like a web server. For this reason, the process is more complicated than what you're probably used to with most installations. Basically, there are more pieces to put together to get everything working.

Should I use a local installation, or one on the internet?
==========================================================

You should use a local installation if:
- you won't have access to the internet at your tournament, or internet access will be flaky
- your tournament is small, doesn't require a public interface and you have a good technical background
- you're involved in or interested in developing Tabbycat

In most cases, you'll want to run Tabbycat on an internet-accessible site. Have a look at [[installing on Heroku]] to see how.

If you're trying out Tabbycat for the first time and just want to see it in action, it's probably easier overall to create a Heroku account and install it on Heroku. But if you're happy to install all the dependencies or want to get more visibility into what's going on, a local installation is also a great way to try it out.

Okay, so how do I do it?
========================

Instructions are here:

- :ref:`install-linux`
- :ref:`install-osx`
- :ref:`install-windows`

.. note:: If you're expecting not to have reliable internet access, be sure to have fully installed Tabbycat **before** you get to your tournament.

Advanced uses
=============

Running a small, isolated network
---------------------------------

Running a local installation doesn't have you mean you don't get the benefits of multi-computer data entry! Your computer is running a web server, and it can serve other computers too. You can do this even if you don't have internet access: all you need is a router that you can use to connect a few computers together. We did this at Victoria Australs 2012.

We don't provide detailed instructions for this; we leave it for advanced users to set up themselves. As a rough guide:

- You need to pass in your computer's IP address and port to the `runserver` command, for example, if your computer (the one acting as a server) is 196.168.0.2 and you want to run it on port 8000: ``dj runserver 192.168.0.2:8000``

- You need to configure your firewall settings to allow incoming connections on the IP address and port you specified in that command.
- Be aware that local installs use the Django development server, whose **security is not tested**. Therefore, it's a good idea to make sure your firewall **only lets in computers on your local network** (or, if you're really paranoid, isolate the network from the internet completely).

Can I run an internet-accessible website from a local installation?
-------------------------------------------------------------------

Probably not. Even if you disable your firewall, chances are your home router (or university router) will block any connections from the outside world to you. Even if you can though, **you really shouldn't**. The local installation uses the *Django development server*, which is a lightweight server designed for developers. Specifically, Django **does not test the security of its development server** in the way that proper web servers do. That is: It's a security risk to run a local installation as an internet-accessible site. Don't do it. [[Install Tabbycat on Heroku|installing on Heroku]] instead.

Alternatively, if you have a background in web development, you might choose to install Tabbycat on your own production server. It's a Django project, so any means of supporting Django projects should work fine.

It's safe to run on a small, isolated network (see above) with your firewall correctly configured because you presumably trust everyone you let on the network!