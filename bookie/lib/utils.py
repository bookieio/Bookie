def parse_bool(value):
    if isinstance(value, bool):
        return value

    return value.lower() in ('1', 'on', 'true')
