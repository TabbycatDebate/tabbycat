<div align="center">

<img width=200 src="https://rawgit.com/TabbycatDebate/tabbycat/develop/tabbycat/static/logo.svg">

# Tabbycat

[![Release](https://img.shields.io/github/release/tabbycatdebate/tabbycat.svg)](https://github.com/tabbycatdebate/tabbycat/releases)
[![Docs](https://readthedocs.org/projects/tabbycat/badge/)](http://tabbycat.readthedocs.io/en/stable/)
[![Build Status](https://travis-ci.org/TabbycatDebate/tabbycat.svg?branch=develop)](https://travis-ci.org/TabbycatDebate/tabbycat)
[![Build status](https://ci.appveyor.com/api/projects/status/hcht4g5x2m5urr8y/branch/develop?svg=true)](https://ci.appveyor.com/project/philipbelesky/tabbycat-81705/branch/develop)
[![Dependenc Status](https://gemnasium.com/badges/github.com/TabbycatDebate/tabbycat.svg)](https://gemnasium.com/github.com/TabbycatDebate/tabbycat)
[![Maintainability](https://api.codeclimate.com/v1/badges/33dc219dfb957ad658c2/maintainability)](https://codeclimate.com/github/TabbycatDebate/tabbycat/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/33dc219dfb957ad658c2/test_coverage)](https://codeclimate.com/github/TabbycatDebate/tabbycat/test_coverage)

</div>

Tabbycat is a draw tabulation system for British Parliamentary and 3 vs 3 debating tournaments. It was used at Australs in 2010, [2012](https://www.facebook.com/Australs2012), [2014](http://australs2014.herokuapp.com), [2015](http://australs2015.herokuapp.com) [2016](http://australs2016.herokuapp.com), and [2017](http://australs2016.herokuapp.com) as well as [many other tournaments of all sizes and formats](http://tabbycat.readthedocs.io/en/stable/about/tournament-history.html). To see an example of a post-tournament website, have a look at the [Australs 2017 tab website](https://australs2017.herokuapp.com/2017_australs/).

**Want to try it out?** The best way to trial Tabbycat is just to launch a new site, as described [in our user guide](https://tabbycat.readthedocs.io/en/stable/install/heroku.html) (or [below](#installation-and-user-guide)). It takes just a few clicks, costs nothing, requires no technical background, and you can always deploy a fresh copy when you're ready to run your tournament.

## 🔍 Features

- Enter data from multiple computers simultaneously and (optionally) display results, draws, and other information online
- Deployable to [Heroku](https://www.heroku.com/) for an easy, fast, and free setup
- Automated adjudicator allocations based on adjudicator ranking, room importance, and conflicts/clashes
- A drag and drop interface for adjudicator allocation that displays conflicts alongside gender and regional balance
- A fully responsive interface that adapts to suit large screens, laptops, tablets, and phones
- Support for British Parliamentary, Australs, NZ Easters, Australian Easters, Joynt Scroll, UADC, and WSDC rule sets as well as configurable [draw generation rules](http://tabbycat.readthedocs.io/en/stable/features/draw-generation.html) and [team standings rules](http://tabbycat.readthedocs.io/en/stable/features/standings-rules.html)
- Configurable [adjudicator feedback questions](http://tabbycat.readthedocs.io/en/stable/features/adjudicator-feedback.html) with (optional) online submission options

## 📖 Installation and Usage

Our user guide is at [tabbycat.readthedocs.io](http://tabbycat.readthedocs.io/). The fastest way to launch a Tabbycat site is to click this button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/TabbycatDebate/tabbycat/tree/master)

During the installation process Heroku will ask you to verify your account by adding a credit or debit card. A standard Tabbycat site *will not charge* your card without explicit permission — charges only accrue if you deliberately add a paid service in the Heroku dashboard.

That said if you do not have access to a credit or debit card we offer a version of the software — 'Tabbykitten' — that does not require Heroku to verify your account. However, as a result, this version is limited: it cannot send emails and cannot be upgraded with extra database capacity or to better handle large amounts of traffic (although you can perform these upgrades later if you verify your Heroku account). We reccomend using it only for small tournaments. [Use this link to set up a Tabbykitten version](https://heroku.com/deploy?template=https://github.com/TabbycatDebate/tabbycat/tree/kitten).

## 💪 Support and Contributing

If you have any feedback or would like to request support, we'd love to hear from you! There are a number of ways to get in touch, all [outlined in our documentation](http://tabbycat.readthedocs.io/en/latest/about/support.html).

Contributions are welcome, and are greatly appreciated! Details about how to contribute [are also outlined in our documentation](http://tabbycat.readthedocs.io/en/latest/about/contributing.html).

## ©️ Licence

We haven't released Tabbycat under an open-source licence, so there is no formal and general right to use this software. Nonetheless, you're welcome to freely use Tabbycat to help run a debating tournament. However, if your tournament is run as a for-profit or for-fundraising activity a donation to Tabbycat's maintainers is required. More details [are available in our licence information](http://tabbycat.readthedocs.io/en/latest/about/licence.html).

## ✏️ Authors

Tabbycat was authored by Qi-Shan Lim for Auckland Australs in 2010. The current active developers are:

- Philip Belesky ([e-mail](http://www.google.com/recaptcha/mailhide/d?k=01aItEbHtwnn1PzIPGGM9W8A==&c=XWljk2iGokfhziV2Rt4OiKA5uab1vCrnxwXcPUsWgnM=))
- Chuan-Zheng Lee ([e-mail](mailto:czlee@stanford.edu))

Please don't hesitate to contact us with any questions, suggestions, or generally anything relating to Tabbycat.
