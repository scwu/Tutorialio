from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns("app.views",
    url("^rooms/$", "rooms", name="rooms"),
    url("^create/$", "create", name="create"),
    url("^system_message/$", "system_message", name="system_message"),
    url("^(?P<slug>.*)$", "room", name="room"),
)
