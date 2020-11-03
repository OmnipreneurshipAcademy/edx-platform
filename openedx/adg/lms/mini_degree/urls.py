"""
All urls for mini_degree app
"""

from django.urls import path

from openedx.adg.lms.mini_degree.views import AddMiniDegreeView, \
     DeleteMiniDegreeView, EditMiniDegreeView, MiniDegreeListView

app_name = 'mini_degree'
urlpatterns = [
    path('add_degree', AddMiniDegreeView.as_view(), name='add_degree'),
    path('edit_degree/<int:pk>', EditMiniDegreeView.as_view(), name='edit_degree'),
    path('delete_degree/<int:pk>', DeleteMiniDegreeView.as_view(), name='delete_degree'),
    path('degrees', MiniDegreeListView.as_view(), name='degrees'),
]
