import json
from django.shortcuts import render
# from django.utils.safestring import mark_safe


def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    print("room name is", room_name)
    return render(request, "chat/room.html", {
        "room_name_json":room_name
        })
