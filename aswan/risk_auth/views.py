#!/usr/bin/env python3
# coding: utf-8

from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from aswan.risk_auth.forms import AuthenticationForm
from aswan.permissions.permission import UserPermission


class Home(TemplateView):
    template_name = 'risk_auth/index.html'


def risk_login(request):
    next_url = request.GET.get("next", None) or reverse("risk_auth:home")
    is_auth = request.user.is_authenticated
    if is_auth:
        return redirect(next_url)

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            user = request.user
            if not UserPermission.objects.get(user.email):
                superuser_flag = user.is_superuser
                UserPermission(
                    user.email,
                    fullname='{}{}'.format(user.last_name, user.first_name) or user.email,
                    is_superuser=superuser_flag
                ).save()
            return redirect(next_url)
    else:
        form = AuthenticationForm()
        form.fields["username"].help_text = _("Please log in")
    context = {"form": form}
    return render(request, 'risk_auth/login.html', context=context)


def risk_logout(request):
    logout(request)
    next_url = reverse("risk_auth:risk_login")
    return redirect(next_url)
