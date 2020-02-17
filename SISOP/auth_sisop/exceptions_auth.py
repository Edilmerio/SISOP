class DatosNoValidos(Exception):
    def __init__(self, mensaje):
        self.mensaje = mensaje


class ServerAuthError(Exception):
    def __init__(self, mensaje):
        self.mensaje = mensaje

