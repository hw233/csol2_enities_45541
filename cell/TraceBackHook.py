# -*- coding: gb18030 -*-
import sys
def handle_exception(exc_type, exc_value, exc_traceback):
    import sys
    import Monster
    import Pet
    import Resource
    import SpaceNormal
    tb = exc_traceback
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

    infos = []
    while tb is not None:
        f = tb.tb_frame
        if f.f_locals.has_key("self"):
            info = ""
            if isinstance(f.f_locals['self'], Monster.Monster):
                info =  "----(Monster," + f.f_locals["self"].className + ")"
            elif isinstance(f.f_locals['self'], Pet.Pet):
                info = "----(Pet," +  f.f_locals["self"].uname + ")"
            elif str(f.f_locals['self']).find("Role") != -1:
                info = "----(Role," + f.f_locals["self"].playerName + ")"
            elif isinstance(f.f_locals['self'],SpaceNormal.SpaceNormal) :
                info = "----(Space," + f.f_locals["self"].className + ")"
            elif str(f.f_locals['self']).find("Skills") != -1:
                info = "----(Skill," +  str(f.f_locals["self"].getID()) + ")"
            if info != "":
                infos.append(info)
        tb = tb.tb_next
    infos = list(set(infos))
    if len(infos) != 0:
        print "Traceback (most recent call last):"
    for v in infos:
        print v
    if len(infos) != 0:
        print "TypeError: " + str(exc_value)


sys.excepthook = handle_exception

    
