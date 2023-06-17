import h2p


class FrameFactory:
    def __new__(cls, name, kwargs):
        items = name.split("_")
        clazz_name = ""
        for item in items:
            clazz_name += item.capitalize()
        clazz_name += "Frame"
        clazz = getattr(h2p.frames, clazz_name)
        return clazz(**kwargs)
