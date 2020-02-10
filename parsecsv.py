import csv

with open("local.csv", "r", encoding='utf-8') as f_obj:
    with  open("localtable.py", "w", encoding='utf-8') as g_obj:
        reader = csv.reader(f_obj)
        res = list()
        g_obj.write("local_table = {")
        for row in reader:
            if row[0]:
                new = {row[0]:{'en': row[1], 'ru': row[2], 'jp': row[3]}}
                line = str(new)[1:-1]
                g_obj.write(" "*15+line+',\n')
        g_obj.write("}")


