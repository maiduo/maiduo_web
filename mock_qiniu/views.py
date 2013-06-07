from django.http import HttpResponse
from django.conf import settings

def key(request):
    if request.method == "POST":
        key_name = request.POST.get("key", "")
        f = request.FILES.get("file")

        return HttpResponse("OK")
