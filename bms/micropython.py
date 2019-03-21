# Hack for testing so that micropython decorators work

def native(f, *args, **kwargs):
    return f