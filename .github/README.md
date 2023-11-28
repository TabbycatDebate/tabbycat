<div align="center">

<img width=200 src="https://raw.githubusercontent.com/TabbycatDebate/tabbycat/develop/tabbycat/static/logo.svg?sanitize=true">

# Tabbycat

[![Release](https://img.shields.io/github/release/tabbycatdebate/tabbycat.svg)](https://github.com/tabbycatdebate/tabbycat/releases)
[![Crowdin](https://badges.crowdin.net/tabbycat/localized.svg)](https://crowdin.com/project/tabbycat)
[![Docs](https://readthedocs.org/projects/tabbycat/badge/)](http://tabbycat.readthedocs.io/en/stable/)
![Build Status](https://github.com/TabbycatDebate/tabbycat/workflows/Django%20CI/badge.svg)
[![Maintainability](https://api.codeclimate.com/v1/badges/33dc219dfb957ad658c2/maintainability)](https://codeclimate.com/github/TabbycatDebate/tabbycat/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/33dc219dfb957ad658c2/test_coverage)](https://codeclimate.com/github/TabbycatDebate/tabbycat/test_coverage)

</div>

Tabbycat is a draw tabulation system for British Parliamentary and a variety of two-team formats. It was used at Australs 2010 and 2012–2019, EUDC 2018, WUDC 2019–2022 and many other tournaments of all sizes and formats. To see an example of a post-tournament website, have a look at the [WUDC 2022 tab website](https://wudc2022.calicotab.com/wudc/).

**Want to try it out?** The best way to trial Tabbycat is just to launch a new site, as described [below](#%EF%B8%8F-installation)). It takes just a few clicks, requires no technical background, and you can always deploy a fresh copy when you're ready to run your tournament.

## 🔍 Features

- A range of setup options. Tabbycat powers Calico, a paid service for hosting tournaments. Tabbycat can also run as a local installation (natively, or via Docker) and be deployed to the free-tiers of the Render or Heroku platforms.
- Enter data from multiple computers simultaneously and (optionally) display results, draws, and other information online
- Collect ballots and feedback online, or from printed forms customised for each round ( adjudicator feedback questions and rankings [are configurable](http://tabbycat.readthedocs.io/en/stable/features/adjudicator-feedback.html))
- Automated adjudicator allocations based on adjudicator ranking, debate priority, and conflicts/clashes
- A drag and drop interface for adjudicator allocation that displays conflicts alongside break liveness and gender/regional/language balance considerations
- A responsive interface that adapts to suit large screens, laptops, tablets, and phones
- Support for British Parliamentary (EUDC/WUDC), Australs, NZ Easters, Australian Easters, Joynt Scroll, UADC, and WSDC rule sets as well as configurable [draw generation rules](http://tabbycat.readthedocs.io/en/stable/features/draw-generation.html) and [team standings rules](http://tabbycat.readthedocs.io/en/stable/features/standings-rules.html)

## 📖 Documentation

Our user guide is at [tabbycat.readthedocs.io](http://tabbycat.readthedocs.io/).

## ⬆️ Installation

Tabbycat can be used in a number of ways.

[Calico](https://calicotab.com/) is a managed hosting service run by one of Tabbycat's developers. For a flat fee, it will host tab websites, automatically manage their setup and performance, and provide ongoing access to the released tab. Click this button to deploy to Calico:

[![Deploy](https://raw.githubusercontent.com/gist/tienne-B/fc04ecd3c11a38424b642b4bba60e8d9/raw/b2c71d7d6a0d368d3e9dfd8002af729d155ad09b/calicodeploy.svg)](https://calicotab.com/tournaments/new/)

If you do not want to use Calico, you will need to setup and manage your own copy of Tabbycat:

1. For tournaments that require online access, you can [install and run Tabbycat from Heroku](https://tabbycat.readthedocs.io/en/stable/install/heroku.html). However, this will cost a small amount of money _unless_ you are a student and have registered for free Heroku hosting credits
2. For tournaments where online access is unnecessary, you can [install and run Tabbycat from your own computer](https://tabbycat.readthedocs.io/en/stable/install/local.html)

## 💪 Support and Contributing

If you have any feedback or would like to request support, we'd love to hear from you! There are a number of ways to get in touch, all [outlined in our documentation](http://tabbycat.readthedocs.io/en/latest/about/support.html).

Contributions are welcome, and are greatly appreciated! Details about how to contribute [are also outlined in our documentation](http://tabbycat.readthedocs.io/en/latest/about/contributing.html).

Monetary donations are much appreciated and help us to continue the development and maintenance of Tabbycat. We suggest that tournaments donate at the level of C$1 (1 Canadian dollar) per team; especially if your tournament is run for profit or fundraising purposes. More details [are available in our documentation](http://tabbycat.readthedocs.io/en/latest/about/licence.html).

## ©️ Licence

Tabbycat is licensed under the terms of the [GNU Affero General Public License v3.0](https://choosealicense.com/licenses/agpl-3.0/). You may copy, distribute, and modify this software; however note that this licence requires (amongst other provisions) that any modifications you make to Tabbycat be made public.

If you wish to modify Tabbycat in a proprietary fashion we (the developers) are open to negotiating a dual licence for this purpose. Please [contact us](http://tabbycat.readthedocs.io/en/latest/authors.html#authors) if this is the case for you.

## ✏️ Authors

Tabbycat was authored by Qi-Shan Lim for Auckland Australs in 2010. The current active developers are:

- Philip Belesky
- Chuan-Zheng Lee
- Étienne Beaulé

Please don't hesitate to contact us ([e-mail](mailto:contact@tabbycat-debate.org)) with any questions, suggestions, or generally anything relating to Tabbycat.
