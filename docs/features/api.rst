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

The schema is available on `Swagger <https://app.swaggerhub.com/apis/tienne-B/tabbycat-api/1.0.0>`_. The OpenAPI schema is also available in the ``docs`` directory of Tabbycat.
