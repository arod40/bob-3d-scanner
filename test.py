class calibration:
    prop_types={
        "threshold":int,
        "slope":float,
        "intercept":float,
        "axis_line":int,
        "laser_dist":float,
        "pltfrm_dist":float,
        "top":int,
        "left":int,
        "right":int,
        "bottom":int,
        "filename":str
    }

    def __init__(self, path=None):
        if path:
            config=open(path)
            for line in config.readlines():
                line=line[:-1] if line[-1]=='\n' else line
                splt=line.split(':')
                property=splt[0]
                value=calibration.prop_types[splt[0]](splt[1])
                self.__setattr__(property,value)

    def save_in_file(self, path=None):
        path=path if path else self.filename+"_calibration"
        fd=open(path,'x')
        for key in self.__dict__:
            fd.write(key+":"+str(self.__dict__[key])+"\n")




cal=calibration("b.txt")
print(cal.__dict__)
cal.save_in_file()

