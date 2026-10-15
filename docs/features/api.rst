.. _api:

=================================
Application Programming Interface
=================================

In conjunction with the public-facing interface of Tabbycat, there is also an Application Programming Interface (or *API*), which provides access to Tabbycat for external applications. For that, the API sends and receives data in a structured format for easy handling.

Accessing the API
======================

The entry-point to the API is through ``/api``. The API endpoints are based on REST and use HATEOAS principles, providing hyperlinks to other resources starting at the entry-point. While this page does not document all the endpoints available, the ``HEAD`` HTTP verb can be used on all endpoints to retrieve the request and response formats. Currently, data must be sent as JSON and will be sent in that format as well.

Administrator vs public access
==============================

Depending on what the external application does, it may require administrator access, or the publicly accessible information suffices. The administrator endpoints may not just retrieve (``GET``) data; they can also change data, such as adding new participants or marking teams as break-eligible. To grant administrator access to an application, you can give it your token, which can be found under *Tokens* in the database or under *Change Password* on the site home page. Each user has a token automatically generated when registered but may have to be manually generated in the *Edit Database* area if upgrading from an older version.

When crafting requests, the token can be passed through HTTP headers in this format: ``Authorization: Token 938fab3...``, replacing the truncated code with your token.

.. note:: Tokens can also be revoked by deleting them in the database area, which will stop the external applications from making further changes.

The API can be disabled in its entirety over an instance through the *Enable API* preference in the *Global Settings* section of the tournament options. This will prevent all authentication and all access, including administrator access, to all API endpoints.

Unauthenticated (public) endpoints are restricted in that they cannot perform modifications. Further, data hidden from the public is also hidden within the API, with access to endpoints and specific fields governed by the tournament's and round's settings. For example, if team codes are used but the participants' list is activated, the team endpoint will be publicly accessible but without showing team names (only codes) nor institutional affiliations.

Schema
======

The API schema documentation can be accessed on Tabbycat instances version 2.8+ through the ``/api/schema/redoc/`` path. The schemas for previous versions can be found in the ``docs`` directory of the Tabbycat repository at version-tagged points.

Updating participant conflicts
==============================

On team and adjudicator detail endpoints, ``PATCH`` adds the relationships in
conflict lists without removing existing ones. To remove specific conflicts,
send their URLs in the corresponding write-only deletion list:

* Teams: ``delete_institution_conflicts``.
* Adjudicators: ``delete_institution_conflicts``, ``delete_team_conflicts``,
  and ``delete_adjudicator_conflicts``.

For example, a ``PATCH`` to ``/api/v1/tournaments/example/adjudicators/42`` can
change affiliation, add a new conflict, and remove a previous conflict together:

.. code-block:: json

   {
     "institution": "https://example.com/api/v1/institutions/2",
     "institution_conflicts": ["https://example.com/api/v1/institutions/2"],
     "delete_institution_conflicts": ["https://example.com/api/v1/institutions/1"]
   }

Changing or clearing institution alone does not add or remove conflicts during
updates. All changes in a participant PATCH are applied atomically. Omitted or
empty deletion lists remove nothing, and removing a valid relationship that is
already absent is a no-op. Adding and deleting the same relationship in one
request is rejected. Invalid URLs and references outside the applicable
tournament are rejected before changes are saved.

Deletion lists are only accepted with ``PATCH`` and are not returned in responses.
Existing ``POST`` detail updates continue to replace explicitly supplied conflict
lists; required full-update fields still apply. ``PUT`` is not exposed on these
endpoints. Conflict handling when initially creating a participant is unchanged.
