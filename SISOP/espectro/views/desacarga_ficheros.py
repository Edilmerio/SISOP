import os
import mimetypes
from wsgiref.util import FileWrapper
from pathlib import Path

from django.http import Http404
from django.http import HttpResponse


class FixedFileWrapper(FileWrapper):
    def __iter__(self):
        self.filelike.seek(0)
        return self


def descargar_ficheros(request):
    """
    Path tine que ser rutas absolutas
    :param request:
    :return:
    """
    path = request.GET.get('dir', '')
    # abs_path = os.path.join(BASE_DIR, path)
    abs_path = os.path.join('/', path)
    archivo = Path(abs_path)
    if not archivo.is_file():
        raise Http404
    response = HttpResponse(FixedFileWrapper(open(abs_path, 'rb')), content_type=mimetypes.guess_type(abs_path)[0])
    response['Content-Length'] = os.path.getsize(abs_path)
    response['Content-Disposition'] = "attachment; filename=%s" % os.path.basename(path)
    # print(abs_path)
    # response['Content-Encoding'] = encoding
    return response

