import csv
import pandas as pd
from main import Cafe,db


def d():
    all_c = db.session.query(Cafe).all()

    dic = {}
    for i in all_c:
        dic[i.name] = i.name

    print(dic)



