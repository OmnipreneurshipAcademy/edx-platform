from django.conf.urls import include, url

adg_url_patterns = [

    # ADG Applications app
    url(
        r'^application/',
        include('openedx.adg.lms.applications.urls'),
    ),

    url(
        r'^bootcamps/',
        include('openedx.adg.lms.bootcamps.urls'),
    )
]
