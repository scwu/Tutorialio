# Create your views here.
#HP Django stuff
from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django_socketio import broadcast, broadcast_channel, NoSocket

from app.models import ChatRoom

#HP app-specific stuff
from app.models import *
from app.forms import *
import settings, urls

#HP everything else (these are usually useful)
import os, sys, datetime, json
# from bootstrap.forms import BootstrapModelForm, Fieldset

#HP:
def hackpackify(request, context):
  '''
  Updates a view's context to include variables expected in base.html
  Intended to make boilerplate info conveyance and menu bars quick and easy.
  and returns a RequestContext of the resulting dict (which is usually better).

  CHANGE EVERYTHING IN THIS!
  '''
  pages = []
  for urlpat in urls.urlpatterns:
    if urlpat.__dict__.__contains__('name'):
      if '(' not in urlpat.regex.pattern:
        pages.append({'name':urlpat.name, 'url':urlpat.regex.pattern.replace('^','/').replace('$','')})

  #HP project_name is used in navbar, copyright (footer), about page, and <title>
  project_name = "A Django HackPack Project"

  #HP project_description is used in <meta name="description"> and the about page.
  project_description = "A super cool app."

  #HP Founder information is in popups linked from the footers, the about page, and <meta name="author">
  founders = [
    {'name':'Alex Rattray',
       'email':'rattray@wharton.upenn.edu',
       'url':'http://alexrattray.com/',
       'blurb':'I\'m Alex. I like webdev and most things Seattle.',
       'picture':'http://profile.ak.fbcdn.net/hprofile-ak-ash2/273392_515004220_1419119046_n.jpg'},
    {'name':'Greg Terrono',
       'email':'gterrono@seas.upenn.edu',
       'url':'http://twitter.com/',
       'blurb':'I\'m Greg. I like webdev and most things Boston. And Dogs.',
       'picture':'http://chucknorri.com/wp-content/uploads/2011/03/Chuck-Norris-14.jpg'},
    ]
  hackpack_context = {
      'pages': pages,
      'project_name': project_name,
      'founders': founders,
      'project_description': project_description,
      }
  if not context.__contains__('hackpack'):
    #HP add the hackpack dict to the page's context
    context['hackpack'] = hackpack_context

  return RequestContext(request, context) #HP RequestContext is good practice. (I think).

def index(request):
  message = 'hello world!' #HP just used for example. Don't do this.
  context = {
    'thispage': 'Home', #HP necessary to know which page we're on (for nav). Always spell the same as the 'Name' field in hackpackify()'s `pages` variable
    'message':message,
  }
  return render_to_response('index.html', hackpackify(request, context))

def about(request):
  context = {
    'thispage':'About', #HP necessary to know which page we're on (for nav). Always spell the same as the 'Name' field in hackpackify()'s `pages` variable
  }
  return render_to_response('about.html', hackpackify(request, context))

def rooms(request, template="rooms.html"):
    """
    Homepage - lists all rooms.
    """
    context = {"rooms": ChatRoom.objects.all()}
    return render(request, template, context)


def room(request, slug, template="room.html"):
    """
    Show a room.
    """
    context = {"room": get_object_or_404(ChatRoom, slug=slug)}
    return render(request, template, context)


def create(request):
    """
    Handles post from the "Add room" form on the homepage, and
    redirects to the new room.
    """
    name = request.POST.get("name")
    if name:
        room, created = ChatRoom.objects.get_or_create(name=name)
        return redirect(room)
    return redirect(rooms)


@user_passes_test(lambda user: user.is_staff)
def system_message(request, template="system_message.html"):
    context = {"rooms": ChatRoom.objects.all()}
    if request.method == "POST":
        room = request.POST["room"]
        data = {"action": "system", "message": request.POST["message"]}
        try:
            if room:
                broadcast_channel(data, channel="room-" + room)
            else:
                broadcast(data)
        except NoSocket, e:
            context["message"] = e
        else:
            context["message"] = "Message sent"
    return render(request, template, context)
