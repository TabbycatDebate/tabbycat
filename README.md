<div align="center">

<img width=200 src="https://raw.githubusercontent.com/TabbycatDebate/tabbycat/develop/tabbycat/static/logo.svg?sanitize=true">

# Tabbycat

[![Release](https://img.shields.io/github/release/tabbycatdebate/tabbycat.svg)](https://github.com/tabbycatdebate/tabbycat/releases)
[![Crowdin](https://badges.crowdin.net/tabbycat/localized.svg)](https://crowdin.com/project/tabbycat)
[![Docs](https://readthedocs.org/projects/tabbycat/badge/)](http://tabbycat.readthedocs.io/en/stable/)
[![Build Status](https://travis-ci.org/TabbycatDebate/tabbycat.svg?branch=develop)](https://travis-ci.org/TabbycatDebate/tabbycat)
[![Build status](https://ci.appveyor.com/api/projects/status/hcht4g5x2m5urr8y/branch/develop?svg=true)](https://ci.appveyor.com/project/philipbelesky/tabbycat-81705/branch/develop)
[![Maintainability](https://api.codeclimate.com/v1/badges/33dc219dfb957ad658c2/maintainability)](https://codeclimate.com/github/TabbycatDebate/tabbycat/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/33dc219dfb957ad658c2/test_coverage)](https://codeclimate.com/github/TabbycatDebate/tabbycat/test_coverage)

</div>

Tabbycat is a draw tabulation system for British Parliamentary and 3 vs 3 debating tournaments. It was used at Australs in 2010, and 2012-2018 as well as at EUDC 2018 and [many other tournaments of all sizes and formats](http://tabbycat.readthedocs.io/en/stable/about/tournament-history.html). To see an example of a post-tournament website, have a look at the [Australs 2018 tab website](https://australs2018.herokuapp.com).

**Want to try it out?** The best way to trial Tabbycat is just to launch a new site, as described [in our user guide](https://tabbycat.readthedocs.io/en/stable/install/heroku.html) (or [below](#installation-and-user-guide)). It takes just a few clicks, costs nothing, requires no technical background, and you can always deploy a fresh copy when you're ready to run your tournament.

## 🔍 Features

- Deployable to [Heroku](https://www.heroku.com/) for an easy, fast, and free setup
- Enter data from multiple computers simultaneously and (optionally) display results, draws, and other information online
- Collect ballots and feedback online, or from printed forms customised for each round ( adjudicator feedback questions and rankings [are configurable](http://tabbycat.readthedocs.io/en/stable/features/adjudicator-feedback.html))
- Automated adjudicator allocations based on adjudicator ranking, debate priority, and conflicts/clashes
- A drag and drop interface for adjudicator allocation that displays conflicts alongside break liveness and gender/regional/language balance considerations
- A responsive interface that adapts to suit large screens, laptops, tablets, and phones
- Support for British Parliamentary (EUDC/WUDC), Australs, NZ Easters, Australian Easters, Joynt Scroll, UADC, and WSDC rule sets as well as configurable [draw generation rules](http://tabbycat.readthedocs.io/en/stable/features/draw-generation.html) and [team standings rules](http://tabbycat.readthedocs.io/en/stable/features/standings-rules.html)

## 📖 Documentation

Our user guide is at [tabbycat.readthedocs.io](http://tabbycat.readthedocs.io/).

## ⬆️ Installation

The fastest way to launch a Tabbycat site is to click this button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/TabbycatDebate/tabbycat/tree/master)

During the installation process Heroku will ask you to verify your account by adding a credit or debit card. A standard Tabbycat site *will not charge* your card without explicit permission — charges only accrue if you deliberately add a paid service in the Heroku dashboard.

That said if you do not have access to a credit or debit card we offer a version of the software — 'Tabbykitten' — that does not require Heroku to verify your account. However, as a result, this version is limited: it cannot send emails and cannot be upgraded with extra database capacity or to better handle large amounts of traffic (although you can perform these upgrades later if you verify your Heroku account). We recommend using it only for small tournaments. [Use this link to set up a Tabbykitten version](https://heroku.com/deploy?template=https://github.com/TabbycatDebate/tabbycat/tree/kitten).

Our documentation also provides guides for how to run Tabbycat on your local machine.

## 💪 Support and Contributing

If you have any feedback or would like to request support, we'd love to hear from you! There are a number of ways to get in touch, all [outlined in our documentation](http://tabbycat.readthedocs.io/en/latest/about/support.html).

Contributions are welcome, and are greatly appreciated! Details about how to contribute [are also outlined in our documentation](http://tabbycat.readthedocs.io/en/latest/about/contributing.html).

We also invite new translations of the interface through [Crowdin](https://crowdin.com/project/tabbycat)! Get in touch for access to our translation platform.

## ©️ Licence

We haven't released Tabbycat under an open-source licence, so there is no formal and general right to use this software. Nonetheless, you're welcome to freely use Tabbycat to help run a debating tournament. However, if your tournament is run as a for-profit or for-fundraising activity a donation to Tabbycat's maintainers is required. More details [are available in our licence information](http://tabbycat.readthedocs.io/en/latest/about/licence.html).

## ✏️ Authors

Tabbycat was authored by Qi-Shan Lim for Auckland Australs in 2010. The current active developers are:

- Philip Belesky ([e-mail](mailto:contact@philipbelesky.com))
- Chuan-Zheng Lee ([e-mail](mailto:czlee@stanford.edu))

Please don't hesitate to contact us with any questions, suggestions, or generally anything relating to Tabbycat.
