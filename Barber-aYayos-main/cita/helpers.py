# tu_app/helpers.py
def user_de(obj):
    """
    Devuelve el User asociado, tolerando .user o .usuario.
    """
    return getattr(obj, "user", None) or getattr(obj, "usuario", None)
