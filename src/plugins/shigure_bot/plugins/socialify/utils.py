def parse_dict(d: dict):
    for k, v in d.copy().items():
        if v is None or v is False:
            d.pop(k)
        if v is True:
            d[k] = 1
    return d
