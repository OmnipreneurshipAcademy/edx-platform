"""
Views to show announcements.
"""


from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView , CreateView, DeleteView

from .models import MiniDegree
from .forms import MiniDegreeForm


class AddMiniDegreeView(LoginRequiredMixin, CreateView):
    def get(self, request):
        return render(request, 'mini_degree.html', {'form': MiniDegreeForm()})

    def post(self , request):
        form = MiniDegreeForm(request.POST)
        if form.is_valid():
            degree = form.save(commit=False)
            degree.user = request.user
            degree.save()
            form.save_m2m()
            return HttpResponseRedirect('/mini_degree/degrees')
        return render(request, 'mini_degree.html', {'form': form})


class EditMiniDegreeView(LoginRequiredMixin, UpdateView):
    model = MiniDegree
    template_name = 'mini_degree.html'
    form_class = MiniDegreeForm
    success_url = '/mini_degree/degrees'


class DeleteMiniDegreeView(LoginRequiredMixin, DeleteView):
    model = MiniDegree
    template_name = 'mini_degree_delete.html'
    success_url = '/mini_degree/degrees'


class MiniDegreeListView(LoginRequiredMixin, ListView):
    template_name = 'mini_degree_list.html'
    context_object_name = 'degrees'
    model = MiniDegree
