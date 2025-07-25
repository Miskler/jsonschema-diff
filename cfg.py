
type_map = {
    type(None): 'null',
    bool: 'boolean',
    int: 'integer',
    float: 'number',
    str: 'string',
    list: 'array',
    tuple: 'array',
    dict: 'object'
}

modes = {
    'append': {
        "color": "green",
        "symbol": "+",
    },
    'remove': {
        "color": "red",
        "symbol": "-",
    },
    'replace': {
        "color": "cyan",
        "symbol": "r",
    },
    'no_diff': {
        "color": "reset",
        "symbol": " ",
    }
}
