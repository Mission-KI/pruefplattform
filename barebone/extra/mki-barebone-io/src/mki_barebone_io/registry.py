import mki_barebone_io.dict

EXT_TO_LOADER = {".json": mki_barebone_io.dict.load_dict}

try:
    import mki_barebone_io.ndarray

    EXT_TO_LOADER[".npy"] = mki_barebone_io.ndarray.load_ndarray
except ImportError:
    pass
