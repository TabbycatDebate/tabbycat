.. _draw-generation-bp:

====================
Draw Generation (BP)
====================

The draw generator for British Parliamentary tournaments tries to rotate teams through positions by assigning them positions they've been in less often before the current round.

Summary of options
==================

Options are set in the **Configuration** page as described in :ref:`starting a tournament <starting-a-tournament>`. Options in `italics` with an asterisk are not WUDC-compliant. The recommended options are shown in **bold**.

.. list-table::
  :header-rows: 1
  :stub-columns: 1
  :widths: 20 40 40

  * - Option
    - Description
    - Allowable values
  * - :ref:`Pullup distribution <draw-bp-pullup-distribution>`
    - Where pullup teams get placed
    - - **Anywhere in bracket**
      - *All in the same room*\*
  * - :ref:`Position cost <draw-bp-position-cost>`
    - Which cost function to use to indicate which position profiles are preferred
    - - Simple
      - **Rényi entropy**
      - Population variance
  * - :ref:`Rényi order <draw-bp-renyi-order>`
    - Order of Rényi entropy
    - Any non-negative number (default: **1**, *i.e.* Shannon entropy)
  * - :ref:`Position cost exponent <draw-bp-position-cost-exponent>`
    - Degree to which large position imbalances should be prioritised
    - Any non-negative number (default: **4**)
  * - :ref:`Assignment method <draw-bp-assignment-method>`
    - Algorithm used to assign positions
    - - *Hungarian*\*
      - **Hungarian with preshuffling**

.. _draw-bp-big-picture:

The big picture
===============

To try to achieve position balance, Tabbycat treats the allocation of teams to debates as an `assignment problem <https://en.wikipedia.org/wiki/Assignment_problem>`_. That is, it computes the "cost" of assigning each team to each position in each debate, and finds an assignment of all teams to a position in a debate that minimises the total cost (the sum over all teams).

A simple example
----------------

Here's a small example, to illustrate the idea. Say you have a tournament with 16 teams, and you're about to draw round 4. There are sixteen "places" in the draw: four positions in each of four rooms. Tabbycat calculates the "cost" of putting each team in each place, and puts them in a matrix, like this:

.. role:: q

.. raw:: html

    <style> .q {color: blue; font-weight: bold;} </style>

+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
|    Room   |                Top                |               Second                |                Third               |               Bottom               |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| Position  | OG     | OO     | CG     | CO     | OG      | OO     | CG     | CO      | OG     | OO      | CG     | CO     | OG     | OO      | CG     | CO     |
+===========+========+========+========+========+=========+========+========+=========+========+=========+========+========+========+=========+========+========+
| **A (8)** | 16     | 16     | 16     | :q:`0` | ∞       | ∞      | ∞      | ∞       | ∞      | ∞       | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **B (7)** | 16     | :q:`0` | 16     | 16     | ∞       | ∞      | ∞      | ∞       | ∞      | ∞       | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **C (7)** | 16     | 16     | :q:`0` | 16     | ∞       | ∞      | ∞      | ∞       | ∞      | ∞       | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **D (6)** | 16     | 0      | 16     | 16     | :q:`16` | 0      | 16     | 16      | ∞      | ∞       | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **E (6)** | :q:`0` | 16     | 16     | 16     | 0       | 16     | 16     | 16      | ∞      | ∞       | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **F (6)** | 16     | 16     | 0      | 16     | 16      | 16     | :q:`0` | 16      | ∞      | ∞       | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **G (5)** | ∞      | ∞      | ∞      | ∞      | 16      | :q:`0` | 16     | 16      | ∞      | ∞       | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **H (5)** | ∞      | ∞      | ∞      | ∞      | 16      | 0      | 16     | :q:`16` | ∞      | ∞       | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **I (4)** | ∞      | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      | ∞       | 16     | 16      | :q:`0` | 16     | ∞      | ∞       | ∞      | ∞      |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **J (4)** | ∞      | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      | ∞       | 16     | 16      | 16     | :q:`0` | ∞      | ∞       | ∞      | ∞      |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **K (3)** | ∞      | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      | ∞       | :q:`0` | 16      | 16     | 16     | 0      | 16      | 16     | 16     |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **L (3)** | ∞      | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      | ∞       | 16     | 16      | 0      | 16     | 16     | 16      | :q:`0` | 16     |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **M (3)** | ∞      | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      | ∞       | 16     | :q:`16` | 16     | 0      | 16     | 16      | 16     | 0      |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **N (3)** | ∞      | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      | ∞       | 0      | 16      | 16     | 16     | :q:`0` | 16      | 16     | 16     |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **O (1)** | ∞      | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      | ∞       | ∞      | ∞       | ∞      | ∞      | 16     | 16      | 16     | :q:`0` |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+
| **P (1)** | ∞      | ∞      | ∞      | ∞      | ∞       | ∞      | ∞      | ∞       | ∞      | ∞       | ∞      | ∞      | 0      | :q:`16` | 16     | 16     |
+-----------+--------+--------+--------+--------+---------+--------+--------+---------+--------+---------+--------+--------+--------+---------+--------+--------+

Each "16" is the cost of putting a team in a position it's seen once; each "0" is the cost of putting a team in the position it hasn't. (Details of how this is calculated are :ref:`below <draw-bp-position-cost-section>`.) For example, team A (on 8 points) has been in every position except CO. The ∞'s indicate places where the team isn't allowed to go, because the room isn't in their bracket. For example, the three teams on 6 points (D, E, F) can go in either the top or second room, because any of them can be the pullup team.

The algorithm then chooses entries so that one is selected from each row and one is selected from each column, in a way that minimises the sum of the selected entries. In this case, the selected entries are highlighted in blue. For example, the top room comprises teams E (OG), B (OO), C (CG) and A (CO).

Sometimes, particularly in round 4, it simply isn't possible to "satisfy" everyone. For example, among the top eight teams, five haven't been in OO, but only two can be accommodated within those brackets. In this case, teams B and G got lucky; there are also many other draws that would have incurred the same total cost.

More generally, in most cases, there will be many optimal solutions. To randomise the selection among them, Tabbycat (under default settings) randomly permutes the rows and columns of the matrix before starting the assignment algorithm.

Explanations of options
=======================

.. _draw-bp-pullup-distribution:

Pullup distribution
-------------------

If the number of teams in a bracket is not a multiple of four, it pulls up teams from the next bracket down. The pullup distribution then governs how those teams are paired into the upper bracket.

The available options are as follows:

.. rst-class:: spaced-list

- **Anywhere in bracket:** The pullup teams are treated as if they were any other team in their new bracket. For example, if there are 17 teams in a 10-point bracket, then the three 9-point teams that get pulled up may be paired anywhere in the 10-point bracket, independently of each other. Chance might put them in the same room, but more likely, they will not all be in the same room, so there will be multiple pullup rooms in the 10-point bracket.

- **All in the same room:** All of the pullup teams will be paired into the same room. This means that there will be at most one pullup room per bracket, effectively creating an "intermediate bracket".

.. note:: While it can be argued that the `All in the same room` setting is fairer, it is prohibited by the WUDC constitution. If your tournament follows WUDC rules, you cannot use this setting.

  The teams that get pulled up aren't specifically chosen---they're just assigned as part of the algorithm described :ref:`above <draw-bp-big-picture>`, which optimises for position balance. Tabbycat doesn't support taking anything else into account when choosing pullup teams. (WUDC rules wouldn't allow it, either.)

.. _draw-bp-position-cost-section:

Position cost options
---------------------

The `position cost function` is a function that indicates how "bad" it would be if a team were to be allocated a certain position (OG, OO, CG, CO) in a debate. When generating a draw, Tabbycat chooses from among the draws that minimise the sum of the position costs for each team.

More formally:

.. rst-class:: spaced-list

- A `position history` or just `history` :math:`\mathbf{h}` is a 4-tuple where each element is the number of times a team has already been in the corresponding position. For example, :math:`\mathbf{h} = (0, 2, 1, 1)` means that a team has been in OO twice, CG and CO once each, and hasn't been in OG.
- A cost function :math:`C(\mathbf{h},s)` is a function specifying how "bad" it would be if a team with position history :math:`\mathbf{h}` were assigned the position :math:`s` in the next round.

Tabbycat allows you to choose from a number of different **position cost functions**, as well as a **position cost exponent** :math:`\beta`. Then, when allocating teams to debates, Tabbycat allocates teams to positions :math:`(s_t, t \in\mathcal{T})` to minimise

.. math::

  \sum_{t \in \mathcal{T}} [C(\mathbf{h}_t,s_t)]^\beta

where :math:`\mathcal{T}` is the set of all teams, :math:`\mathbf{h}_t` is the position history of team :math:`t` and :math:`s_t` is the position to which team :math:`t` would be allocated.

.. _draw-bp-position-cost-exponent:

Position cost exponent
^^^^^^^^^^^^^^^^^^^^^^

The **position cost exponent** :math:`\beta` controls how different teams trade off with each other.

.. rst-class:: spaced-list

- The **larger** :math:`\beta` is, the more concerned it is with preventing *very* bad situations. That is, it will give more teams some slight unevenness in order to prevent one team from getting a `very` uneven history.

- The **smaller** :math:`\beta` is, the more concerned it is with preventing *any* unevenness. That is, it will try to keep more teams from being uneven *at all*, at the cost of possibly letting just one team get a very uneven history.

- At the large extreme, as :math:`\beta\rightarrow\infty`, it will do everything it can to minimise the plight of the *worst-off* team, and it won't care for *any* team other than the worst-off.

- At the small extreme, as :math:`\beta\rightarrow 0`, it will do everything it can to minimise the number of teams with a non-optimal profile---but if it's impossible to protect a team from sub-optimality, it won't care *how* uneven the unlucky team gets.

The "balanced" approach would be :math:`\beta = 1`, which just takes the cost function as-is. This doesn't mean that this is the best idea, however---you'd typically want to bias towards preventing very uneven histories a bit more. Most tournaments will probably want :math:`\beta` to be somewhere between 2 and 5.  (Note that :math:`\beta` need not be an integer.)

.. _draw-bp-position-cost:

Position cost functions
^^^^^^^^^^^^^^^^^^^^^^^

Tabbycat allows you to choose between three position cost functions :math:`C(\mathbf{h},s)`: **Simple**, **Rényi entropy** and **Population variance**.

In the descriptions that follow, :math:`\mathcal{S} = \{\texttt{OG}, \texttt{OO}, \texttt{CG}, \texttt{CO}\}`, the set of all BP positions.

Simple
""""""

The simple cost function :math:`C_\textrm{simple}(\mathbf{h},s)` returns the number of times the team has already been in position :math:`s`, less the number of times the team has been in its least frequent position. That is,

.. math::

  C_\mathrm{simple}(\mathbf{h},s) = \mathbf{h}[s] - \min_{s' \in\mathcal{S}} \mathbf{h}[s']

where :math:`\mathbf{h}[s]` is the element of :math:`\mathbf{h}` corresponding to position :math:`s`.

Rényi entropy
"""""""""""""

Informally speaking, the `Rényi entropy <https://en.wikipedia.org/wiki/R%C3%A9nyi_entropy>`_ is a measure of the diversity of the positions in a team's history. A history consisting only of one position has *low* entropy, while a history that is perfectly evenly distributed has *high* entropy. The **Rényi entropy cost function** reverses this intuition, so that an even hypothetical history has low cost, while an uneven hypothetical history has high cost.

The Rényi entropy takes one parameter, known as its *order*, :math:`\alpha`, which will be further discussed below.

More formally, the Rényi entropy cost function :math:`C_\textrm{R\'enyi}(\mathbf{h},s)` is defined as

.. math::

  C_\textrm{R\'enyi}(\mathbf{h},s) = n_\mathbf{h} [2 - H_\alpha(\hat{p}_{\mathbf{h},s})]

where

.. rst-class:: spaced-list

- :math:`n_\mathbf{h} = \sum_{s'} \mathbf{h}[s']` is the number of rounds the team has competed in so far.
- :math:`\hat{p}_{\mathbf{h},s}` is the *normalised hypothetical* position history that would arise if a team with history :math:`\mathbf{h}` were to be allocated position :math:`s` in the next round; that is,

  .. math::

    \hat{p}_{\mathbf{h},s}[s'] = \begin{cases}
      \frac{1}{n_\mathbf{h} + 1} (\mathbf{h}[s'] + 1), &\text{ if } s = s', \\
      \frac{1}{n_\mathbf{h} + 1} \mathbf{h}[s'], &\text{ if } s \ne s'.
    \end{cases}

  Note that :math:`\hat{p}_{\mathbf{h},s}` is a probability distribution (that is, its elements sum to 1).

- :math:`H_\alpha(\cdot)` is the `Rényi entropy <https://en.wikipedia.org/wiki/R%C3%A9nyi_entropy>`_ of order :math:`\alpha` of a probability distribution, defined as

  .. math::

    H_\alpha(p) = \frac{1}{1-\alpha} \log_2 \left( \sum_{s\in\mathcal{S}} (p[s])^\alpha \right), \qquad \alpha \ne 1.

  In the special (limiting) case where :math:`\alpha=1`, it reduces to the `Shannon entropy <https://en.wikipedia.org/wiki/Shannon_entropy>`_,

  .. math::

    H_1(p) =-\sum_{s\in\mathcal{S}} p[s] \log_2 p[s].

  Note that for all :math:`\alpha`, :math:`0 \le H_\alpha(p) \le \log_2(4) = 2` (since there are four positions in BP).

.. _draw-bp-renyi-order:

The **Rényi order** is the parameter :math:`\alpha` above, and it controls *what it means to be "even among positions"* for a team. Note that "evenness" is not easily defined. After round 8, which position history is more even: (0, 2, 3, 3) or (1, 1, 1, 5)? The Rényi order allows us to tune this definition.

.. rst-class:: spaced-list

- The **smaller** :math:`\alpha` is, the more it cares that teams compete in every position *at least* once, favouring (1, 1, 1, 5) over (0, 2, 3, 3): it's worse to have never OGed, than it is to have COed five times.

- The **larger** :math:`\alpha` is, the more it cares that teams do not compete in *any* (one) position too many times, favouring (0, 2, 3, 3) over (1, 1, 1, 5): it's worse to have COed five times, than it is to have never OGed.

- At the small extreme, as :math:`\alpha\rightarrow0`, it *only* counts how many positions a team has seen at least once, and doesn't care about the distribution among them so long as a team has been in each position once.

- At the large extreme, as :math:`\alpha\rightarrow\infty`, it *only* looks at how many times each team has seen its *most frequent* position, and tries to keep this number even among all teams.

The "balanced" approach would be :math:`\alpha=1` (the `Shannon entropy <https://en.wikipedia.org/wiki/Shannon_entropy>`_), though of course it's arguable what "balanced" means. Tabbycat defaults to this value.

To give some intuition for the useful range: In round 9, a strict ordering by number of positions seen at least once occurs for approximately :math:`\alpha < 0.742`. A strict ordering by number of times in the most frequent position occurs for :math:`\alpha>3`. Changing :math:`\alpha` outside the range :math:`[0.742, 3]` will still affect the relative (cardinal) weighting *between teams*, but will not affect the *ordinal* ranking of possible histories.

The purpose of weighting costs by :math:`n_\mathbf{h}` is to prioritise those teams who have competed in every round over those who have competed in fewer rounds.


Population variance
"""""""""""""""""""

The **population variance** cost function is just the population variance of the history 4-tuple,

.. math::

  C_\textrm{popvar}(\mathbf{h},s) = \frac14 \sum_{s'\in\mathcal{S}} \left(\mathbf{\hat{h}}_s[s'] - \mu_{\mathbf{\hat{h}}_s} \right)^2,

where :math:`\mathbf{\hat{h}}_s` is the *hypothetical* position history that would arise if a team with history :math:`\mathbf{h}` were to be allocated position :math:`s` in the next round; that is,

  .. math::

    \mathbf{\hat{h}}_s[s'] = \begin{cases}
      \mathbf{h}[s'] + 1, &\text{ if } s = s', \\
      \mathbf{h}[s'], &\text{ if } s \ne s'.
    \end{cases}

and where :math:`\mu_{\mathbf{\hat{h}}_s}` is the mean of :math:`\mathbf{\hat{h}}_s`,

.. math::

  \mu_{\mathbf{\hat{h}}_s} = \frac14 \sum_{s'\in\mathcal{S}} \mathbf{\hat{h}}_s[s'].

At the extremes, a team that has seen all positions evenly will have a population variance of zero, while a team that has seen just one position :math:`n` times will have a population variance of :math:`\frac{3n^2}{16}`.

.. _draw-bp-assignment-method:

Assignment method
-----------------

Tabbycat uses the `Hungarian algorithm <https://en.wikipedia.org/wiki/Hungarian_algorithm>`_ to solve the `assignment problem <https://en.wikipedia.org/wiki/Assignment_problem>`_ of assigning teams to positions in debates. This can be run with or without preshuffling:

.. rst-class:: spaced-list

- **Hungarian algorithm** just runs the Hungarian algorithm as-is, with no randomness. This probably isn't what you want.

- **Hungarian algorithm with preshuffling** also runs the Hungarian algorithm on the position cost matrix, but shuffles the input so that the draw is randomised, subject to having optimal position allocations.

  Preshuffling doesn't compromise the optimality of position allocations: It simply shuffles the order in which teams and debates appear in the input to the algorithm, by randomly permuting the rows and columns of the position cost matrix. The Hungarian algorithm still guarantees an optimal position assignment, according to the chosen position cost function.

.. note:: Running the Hungarian algorithm *without* preshuffling has the side effect of grouping teams with similar speaker scores in to the same room, and is therefore prohibited by WUDC rules. Its inclusion as an option is mainly academic; most tournaments will not want to use it in practice.

No other assignment methods are currently supported. For example, Tabbycat can't run fold (high-low) or adjacent (high-high) pairing *within* brackets.
