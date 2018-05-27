import sys, time, os, re, string, sqlite3
from glob import glob
import calendar
abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}

conn = sqlite3.connect('femjoy.db')
setsdb = conn.cursor()
conn.execute('delete from sets')

files = []
start_dir = r'Z:\femjoy'
pattern   = "cover2*.jpg"

def sqlite_insert(conn, table, row):
    cols = ', '.join('"{}"'.format(col) for col in row.keys())
    vals = ', '.join(':{}'.format(col) for col in row.keys())
    sql = 'INSERT INTO "{0}" ({1}) VALUES ({2})'.format(table, cols, vals)
    conn.cursor().execute(sql, row)
    conn.commit()

for dir,_,_ in os.walk(start_dir):
    files.extend(glob(os.path.join(dir,pattern)))

# print files
#
for f in files:
    thumb = os.path.basename(f)
    subdir = os.path.split(os.path.dirname(f))[1]
    # print subdir
    day, model, setname = subdir.split(' - ')
    month = os.path.split(os.path.split(os.path.dirname(f))[0])[1]
    # month = abbr_to_num[monthname]
    # if month < 10:
        # month = '0'+str(month)
    # else:
        # month = str(month)
    year = os.path.split(os.path.split(os.path.split(os.path.dirname(f))[0])[0])[1]
    # print year
    dir = '/femjoy/'+year+'/'+month+'/'+subdir+'/'
    thumb = '/femjoy/'+year+'/'+month+'/'+subdir+'/'+os.path.basename(f)
    date = year+month+day
    print thumb
    sqlite_insert(conn, 'sets', {'model': model, 'thumb': thumb, 'directory': dir, 'date': date, 'photographer': '', 'rating': 0, 'video': 0, 'setname': setname})
