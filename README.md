# Tabbycat

Tabbycat is a draw tabulation system for 3 vs 3 debating tournaments. It was used at Auckland Australs 2010, [Victoria Australs 2012](http://australs2012.com) and [Otago Australs 2014](http://australs2014.com).

Our **demo site** is at http://tabbycatdebate.herokuapp.com/. It's normally up, but its form will vary from time to time as we set up new feature demos for people. If it's down and you'd like to see it, or if you want to play with it as if you were running a tournament, contact us (details below). To see a post-tournament website, have a look at the Otago Australs 2014 tab website at http://tab.australs2014.com/.

If you're interested in using, developing or otherwise following this software,
[join our Facebook group](https://www.facebook.com/groups/tabbycat.debate/) and/or contact us (details below).

## Features

- Enter data from multiple computers simultaneously
- Easily deployable to [Heroku](https://www.heroku.com) for a super fast setup
- Automated adjudicator allocations based on adjudicator ranking, room importance, and conflicts
- A drag and drop interface for adjudicator allocation that automatically displays conflicts
- Responsive templates designed for large screens, laptops, tablets, and phones
- Configurable [draw generation rules](https://github.com/czlee/tabbycat/wiki/Draw-generation)
- Supports Australs and NZ [team standings rules](https://github.com/czlee/tabbycat/wiki/Team-standings-rules)
- Optional online ballot submission
- Optional online post-tournament tab display

#### Something missing?

The system's currently optimized for Australs, but we're developing for all two-team formats. So if your tournament has different requirements to what we have (say, different draw rules or number of speakers), odds are we've already thought about it and it's on the [to-do list](https://github.com/czlee/tabbycat/issues).

That said, our to-do list is long. **We prioritise our work by the features that will be used first.** So if you're planning to use it for a tournament but need some changes, please don't be shy—get in touch with us (below) and we'll be more than happy to help. Please don't just wait for us to implement your requirement: we'd rather have the real-time feedback about which features are most useful!

## Installation and user guide
All installation instructions and user guidelines are on the [wiki for this repository](https://github.com/czlee/tabbycat/wiki/).

#### Assisted setup

If you want to run a tournament with Tabby Cat but are not able to set it up, get in touch with [Philip](http://www.google.com/recaptcha/mailhide/d?k=01aItEbHtwnn1PzIPGGM9W8A==&c=XWljk2iGokfhziV2Rt4OiKA5uab1vCrnxwXcPUsWgnM=) and he can setup a private and online copy of the software for your use.

#### Directory structure
* `data` contains import data for past tournaments and demonstration tournaments
    * Most directories have data for a particular tournament
    * `utils` contains Python scripts that can be useful for back-end database manipulation, _e.g._ generating random results
* `debate` contains the source code for the app (the real stuff)
    * `adjudicator` contains adjudicator allocation algorithms
    * `management` contains [management scripts](https://docs.djangoproject.com/en/dev/howto/custom-management-commands/) for `manage.py`
    * `templatetags` contains [custom template tags](https://docs.djangoproject.com/en/dev/howto/custom-template-tags/)
    * `tests` contains [unit tests](https://docs.djangoproject.com/en/dev/topics/testing/overview/)
* `static` contains static files
* `templates` contains Django templates

## Licensing, development and contact

We haven't released this under an open-source licence (so there is no formal general right to use this software), but if you're running a debating tournament, you're welcome to use it. It'd be nice if you could please let us know that you're doing so, and let us know how it went. [Our Facebook group](https://www.facebook.com/groups/tabbycat.debate/) is a great place to start. We're happy to help if you have any questions (contact below) or feature requests (see [above](#something-missing)), though obviously we provide no warranty and disclaim all legal liability. Pull requests are encouraged.

Tabbycat was authored by Qi-Shan Lim for Auckland Australs 2010. The current active developers are:
* Philip Belesky ([e-mail](http://www.google.com/recaptcha/mailhide/d?k=01aItEbHtwnn1PzIPGGM9W8A==&c=XWljk2iGokfhziV2Rt4OiKA5uab1vCrnxwXcPUsWgnM=))
* Chuan-Zheng Lee ([e-mail](mailto:czlee@stanford.edu))

Please don't hesitate to contact us with any questions, suggestions, expressions of interest or generally anything relating to Tabbycat.

If you're interested in helping out as a developer, we'd love to have you! [Join our Facebook group](https://www.facebook.com/groups/tabbycat.debate/) and contact us as above.

**Bug reports.** If you have a GitHub account, we'd prefer that bugs be reported to our [issues page](https://github.com/czlee/tabbycat/issues). Otherwise, please contact us as above.
