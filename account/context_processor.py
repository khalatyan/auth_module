
def get_global_context(request):
    user = request.user

    return locals()
