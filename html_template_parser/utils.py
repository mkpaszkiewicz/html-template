def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def convert_strings_to_numbers(collection):
    if isinstance(collection, dict):
        for key, value in collection.items():
            if is_int(value):
                collection[key] = int(value)
            elif is_float(value):
                collection[key] = float(value)
    elif isinstance(collection, list) or isinstance(collection, tuple):
        new_values = []
        for value in collection:
            if is_int(value):
                new_values.append(int(value))
            elif is_float(value):
                new_values.append(float(value))
            new_values.append(float(value))
        collection = new_values
    else:
        raise TypeError()
    return collection
