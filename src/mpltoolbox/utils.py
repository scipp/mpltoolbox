def parse_kwargs(kwargs, number):
    parsed = {}
    for key, value in kwargs.items():
        if callable(value):
            parsed[key] = value()
        elif isinstance(value, list):
            parsed[key] = value[number % len(value)]
        else:
            parsed[key] = value
    return parsed
