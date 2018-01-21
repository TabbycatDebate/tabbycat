from channels import include


# This acts like a urls.py equivalent; need to import the channel routes
# from sub apps into this file (plus specifying their top level URL path)
# Note the lack of trailing "/" (but paths in apps need a trailing "/")

channel_routing = [
    include('actionlog.routing.channel_routing', path=r"^/(?P<tournament_id>[^/]+)/actionlog")
]
