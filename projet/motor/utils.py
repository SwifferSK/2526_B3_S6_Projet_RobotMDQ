
    """
    Convertit un angle en nombre de pas (microsteps inclus)
    """
    return int((angle / 360) * (steps_per_rev * microstep))