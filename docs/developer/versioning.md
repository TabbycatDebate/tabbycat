We follow [Semantic Versioning](http://semver.org/). That said, since this is end-user software, there aren't any downstream dependencies so the concept of a "public API" isn't quite as obvious for Tabbycat as it is for projects more reliant on semantic versioning to manage dependencies. In complying with Semantic Versioning, we consider the following to be our "public API", along with the following criteria for backwards incompatibility:

 - **Database schema**
    - if it cannot be migrated forwards or backwards using the standard migration function without user-input defaults
    - if migration forwards would entail losing data or require reformatting data
 - **Management commands**
    - if a command that used to work no longer works
 - **GUI**
    - if there is a major change to the workflow of any user
 - **Tournament data importer, including tournament configuration**
    - if files that used to work would no longer work.
    - however, with tournament configuration, Tabbycat could in most cases detect deprecated settings and interpret them in any new framework with a warning message.

Starting from version 0.7.0, we use code names for versions, being breeds of cats in alphabetical order.