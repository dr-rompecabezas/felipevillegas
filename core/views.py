from django.conf import settings
from django.http import FileResponse, HttpRequest, JsonResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET


@require_GET
def health_check(request):
    return JsonResponse({"status": "ok"})


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> FileResponse:
    file = (settings.BASE_DIR / "static" / "images" / "favicon-96x96.png").open("rb")
    return FileResponse(file)
