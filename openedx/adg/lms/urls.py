from django.conf.urls import include, url

adg_url_patterns = [

    # ADG Applications app
    url(
        r'^mini_degree/',
        include('openedx.adg.lms.mini_degree.urls'),
    ),
]
