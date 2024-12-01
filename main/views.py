import json
import sqlite3
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from docutils.nodes import table

from Web.settings import DATABASES
from Web.table import get_table, look_in_cell, check_formula


def index(request):
    return render(request, 'main/index.html')


@csrf_exempt
def check_cell(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    data = json.loads(request.body)
    text = data.get("text")
    if text[0] == "=":
        table = get_database(" Revenue")
        return JsonResponse({"success": True, "text": check_formula(text,table)})
    else:
        return JsonResponse({"success": True, "text": ""})



@csrf_exempt
def save_cell(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    data = json.loads(request.body)
    cell_address = data.get("address")
    new_value = data.get("text")

    if not cell_address or new_value is None:
        return JsonResponse({"error": "Invalid data"}, status=400)

    conn = sqlite3.connect(DATABASES["default"]["NAME"])
    cur = conn.cursor()

    df = cur.execute(f"SELECT * FROM {' Revenue'}")
    names = [description[0] for description in df.description]

    col_index = ord(cell_address[0].upper()) - ord('А')+2
    row_id = int(cell_address[1:])

    column_name = names[col_index]
    cur.execute(f'UPDATE  Revenue SET {column_name} = ? WHERE id = ?', (new_value, row_id))

    conn.commit()
    conn.close()

    if len(new_value) > 0 and new_value[0] == "=":
        return JsonResponse({"success": True, "text": str(check_formula(new_value, get_database(" Revenue")))})
    else:
        return JsonResponse({"success": True, "text": new_value})


def get_cell(request):
    table = get_database(" Revenue")
    text = str(look_in_cell(request.GET.get("text"),table))
    if text == "None":
        return JsonResponse({"total_value": ""})
    return JsonResponse({"total_value": text})


def generate_table(request):
    table = get_database(" Revenue")
    return JsonResponse({"table": get_table(table),"rows":len(table),"cols":len(table[0])-1})


def get_database(name_table):
    conn = sqlite3.connect(DATABASES["default"]["NAME"])
    cur = conn.cursor()
    df = cur.execute(f"SELECT * FROM {name_table}")
    table = df.fetchall()
    conn.close()
    return table

def add_new_row(request):
    conn = sqlite3.connect(DATABASES["default"]["NAME"])
    cur = conn.cursor()
    df = cur.execute(f"SELECT * FROM {" Revenue"}")
    sqlite_insert_query = f"""INSERT INTO {" Revenue"}
                              (id)
                              VALUES
                              ({df.fetchall()[-1][0]+1});"""
    cur.execute(sqlite_insert_query)
    conn.commit()
    conn.close()
    return JsonResponse({"success": True})

def add_new_col(request):
    conn = sqlite3.connect(DATABASES["default"]["NAME"])
    cur = conn.cursor()
    df = cur.execute(f"SELECT * FROM {" Revenue"}")
    names = [description[0] for description in df.description]
    cur.execute(f"alter table {" Revenue"} add column `{chr(ord(names[-1].upper())+1)}` TEXT")
    conn.commit()
    conn.close()
    return JsonResponse({"success": True})

# def delete_row(request):
#     conn = sqlite3.connect(DATABASES["default"]["NAME"])
#     cur = conn.cursor()
#     mydata = cur.execute(f"DELETE FROM {" Revenue"} WHERE id=?", (11,))
#     conn.commit()
#     conn.close()
#     return JsonResponse({"success": True})

# def delete_col(request):
#     conn = sqlite3.connect(DATABASES["default"]["NAME"])
#     cur = conn.cursor()
#     cur.execute(f"ALTER TABLE {" Revenue"} DROP COLUMN {'product'}")
#     conn.commit()
#     conn.close()
#     return JsonResponse({"success": True})