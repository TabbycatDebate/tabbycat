# Running a Tournament

Once you've finished the steps in *[Starting a tournament](starting-a-tournament.md)*, you're ready to go! This page outlines what you would do for each round during the tournament. After the tournament, proceed to *[Finishing a tournament](finishing-a-tournament.md)*.

The menu is at the top of the page. In the admin interface, tournament-wide pages and frequently-used round-specific pages for the current round are on the left. Round-specific pages for all rounds are on the right.

![Tabbycat admin menu](/use/images/tabbycat-admin-menu.png)

The workflow for each round is:

1. [Generate the draw](#generating-the-draw)
2. [Release the draw](#releasing-the-draw)
3. Have the debates
4. [Enter results](#entering-results)
5. [Advance to the next round](#advancing-the-current-round)

## Generating the draw

This is all done from an admin interface (*i.e.*, by the tab director or adjudication core member) like so:

1. **Set availability.** For each round, you need to set the venue, team and adjudicator availability. To do this, click the round on the right of the menu, then click **Venue Checkins**, **Adj Checkins** and **Team Checkins** in turn. On each page, edit the availability and click **Save changes**.

    > *__Note__: You don't need to do Participant Checkins. That feature doesn't factor into the draw. It was implemented to replace the roll call with barcode scanning, which you may or may not like to use.*

2. **Generate the draw.** Go to the **Draw** page (at the top-left of the page). Follow the instructions to generate the draw.

    > *__Note:__ Tabbycat will show you a draft draw before you confirm it. In the draft draw, it'll show you details so that you can understand how it came up with the draw, pointing out pull-ups and conflict swaps and the like. This is for you to double-check. While there are some basic tests on the draw algorithm, it never hurts to sanity-check it again. But you can't actually modify the draw from the user interface, and we've never needed to.*

    > *__Note:__ If you *do* find something wrong with a draft draw, the only remedy is to edit the database directly. See [Draw generation](../features/draw-generation.md) for instructions.*

3. After the draft draw has been confirmed, it will show the confirmed draw page. Click **Edit adjudicators** and allocate adjudicators. It's a good idea to save periodically, in case something goes wrong or you want to revert.

## Releasing the Draw

Once you're happy with your adjudicator allocation, you're ready to start the round.

1. **Release to general assembly.** From the (confirmed) *Draw* page, go to **Show by Venue** or **Show by Team** (whichever you prefer). Then put it up on the projector. There are automatic scroll buttons.

    > *__Note__: The main *Draw* page shows a ranked draw, *i.e.* teams can infer their position on the tab from the version on the admin interface. Unless you want to spare teams the fun of backtabbing, you probably don't want them to see this. So you should turn the projector off before you log in to Tabbycat on the projected computer, and only turn it on once you have the *Show by Venue* or *Show by Team* draw up.*

    > *__Note:__ If you find the slowest scroll button too slow, or the fastest one too fast, please let us know.*

    > *__Note:__ To avoid the site from being overloaded by anxious refreshers, we recommend not releasing the draw to the public until after it's been seen by general assembly.*

2. **Release to public.** If you're using the public draw function, use the **Release to Public** button to publicly display the draw page.

3. **Release motions to general assembly.** Release the motions however you would normally release the motions. (Tabbycat won't do this for you.)

4. **Enter and release motions.** Enter the motion(s) for each round on the Motions page, then use the **Release Motions to Public** button to publicly display them.
    > Note: Currently, it's mandatory to enter motions into the system. (You don't have to release them, just enter them.) We eventually intend to make it optional, but this is low priority. If you'd like it to be optional, please get in touch with us and we'll accord it higher priority.

5. Entering results. See [Data entry](../features/data-entry.md) for more details about this process.

6. Enter debate results and feedback as they come in (and/or allow online entry of results and feedback).

7. Both results and feedback entered in the tab room or online need to be confirmed before the results are counted. To confirm a debate ballot and the debate as a whole, the confirmed checkbox under *Ballot Status* should be ticket in addition to the *Debate Status* being set to Confirmed.

You can track data entry from the **Status** page in an admin account.

> *Warning! For major tournaments, we don't recommend entering any data from an admin's account. This is because the admin interface (intentionally) does not enforce the data confirmation procedure.*

## Moving to the Rext Round

Once you've got all the results entered and confirmed, you're ready to progress to the next round. This can be done by going to the **Status** area, and then using the **Advance** button.

> *__Warning!__ When you advance to the next round, if you've enabled public results, the results for the current round (which is now the previous round) will be release to the public **unless** the round is marked as "silent" in the database. So if you're careful about when results should be released, don't change the current round until you're ready to release those results.*

> *__Note:__There is a design assumption that you will always want to release results for non-silent rounds before you start working on the draw for the next round. If this isn't true for you, please get in touch with us so that we know. The workaround is to make all rounds silent, then unsilent them when you're ready to release results.*

