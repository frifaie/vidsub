from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView

import stripe

from .models import Membership, UserMembership, Subscription

def get_user_membership(request):
    try:
        user_membership_qs = UserMembership.objects.get(user=request.user)
        return user_membership_qs
    except ObjectDoesNotExist:
        return None

def get_user_subscription(request):
    try:
        user_subscription_qs = Subscription.objects.filter(user_membership=get_user_membership(request))
        return user_subscription_qs
    except ObjectDoesNotExist:
        return None

def get_selected_membership(request):
    membership_type = request.session['selected_membership_type']
    selected_membership_qs = Membership.objects.filter(membership_type=membership_type)
    if selected_membership_qs.exists():
        return selected_membership_qs[0]
    else:
        return None

class MembershipSelectView(ListView):
    model = Membership

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_membership = get_user_membership(self.request)
        context['current_membership'] = str(current_membership.membership)
        return context

    def post(self, request, **kwargs):
        selected_membership_type = request.POST.get('membership_type')
        user_membership = get_user_membership(request)
        user_subscription = get_user_subscription(request)
        selected_membership_qs = Membership.objects.filter(membership_type=selected_membership_type)
        if selected_membership_qs.exists():
            selected_membership = selected_membership_qs[0]


        if user_membership.membership == selected_membership:
            if user_subscription != None:
                messages.info(request, 'This is your membership')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        request.session['selected_membership_type'] = selected_membership.membership_type
        return HttpResponseRedirect(reverse('memberships:payment'))

def PaymentView(request):
    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership(request)
    publishKey = settings.STRIPE_PUBLISHABLE_KEY



