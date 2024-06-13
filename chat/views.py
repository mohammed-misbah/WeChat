import json
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, "chat/index.html")


@login_required
def room(request, room_name):
    username = request.user.username
    return render(request, "chat/room.html", {"room_name": room_name, "username": username})

# def room(request, room_name):
#     return render(request, 'chat/room.html', {
#         'room_name_json': mark_safe(json.dumps(room_name)),
#         'username': mark_safe(json.dumps(request.user.username)),
#     })
