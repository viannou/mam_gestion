# -*- coding: utf8 -*-
from datetime import datetime,date,timedelta
import re

def verif_heures(hdebut, hfin, fin_obligatoire=False):
    try:
        matchObj = re.match( r"^(\d+?)[- _.:;'hH]?(\d{1,2})[mM]?$",  hdebut)
        if matchObj:
            hdebut = "{:%H:%M}".format(datetime.strptime(matchObj.group(1)+":"+matchObj.group(2),"%H:%M"))
        else:
            return False
        if not fin_obligatoire and (hfin == False or hfin == ""):
            return [hdebut,""]
        matchObj = re.match( r"^(\d+?)[- _.:;'hH]?(\d{1,2})[mM]?$",  hfin)
        if matchObj:
            hfin = "{:%H:%M}".format(datetime.strptime(matchObj.group(1)+":"+matchObj.group(2),"%H:%M"))
        else:
            return False
        return [hdebut,hfin]
    except:
        return False

def conv_str2minutes(str):
    if ":" in str:
        (h,m) = str.split(":") # 11:45
    else:
        (h,min) = str.split("h ") # 3h 30m
        m=min[:2]
    return (int(h)*60 + int(m))
def conv_minutes2str(min):
    return "{0}h {1:02d}m".format(min/60, min%60) # 3h 30m