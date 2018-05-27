import sys, time, os, re, string, sqlite3, subprocess, datetime
from glob import glob
from docopt import docopt
import cv2
from PIL import Image
from click import progressbar
import os, random, shutil, math, tempfile
import imageio

import urllib2

def downloadfile(url,file_name):
    # url = "http://download.thinkbroadband.com/10MB.zip"

    # file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()

TMP_FRAMES_PATH = './wowframes/'

def generate_video_thumbnail(video):
    print video
    generate_video_thumbnail_file(video)

def generate_video_thumbnail_file(video):
    videoFileClip = video
    interval = 50
    size = 250, 250
    output = video+'.gif'
    outputPrefix = get_output_prefix()
    if not os.path.isfile(output):
        try:
            generate_frames(videoFileClip, interval, outputPrefix, size)
            columns = 1
            # output = args['<output>']
            generate_sprite_from_frames(outputPrefix, columns, size, output)
        except:
            pass

def generate_frames(videoFileClip, interval, outputPrefix, size):
    # print "Extracting", int(videoFileClip.duration / interval), "frames"
    frameCount = 0
    cap = cv2.VideoCapture(videoFileClip)
    totalframes = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    interval = int(totalframes / interval)
    with progressbar(range(0, int(totalframes), interval)) as items:
        for i in items:
            extract_frame(cap, i, outputPrefix, size, frameCount)
            frameCount += 1
    print "Frames extracted."

def extract_frame(cap, moment, outputPrefix, size, frameCount):
    output = outputPrefix + ("%05d.png" % frameCount)
    cap.set(cv2.CAP_PROP_POS_FRAMES,moment)
    ret,frame = cap.read()                   # Retrieves the frame at the specified second
    if ret:
        cv2.imwrite(output, frame)
        resize_frame(output, size)

def resize_frame(filename, size):
    image = Image.open(filename)
    image.thumbnail(size)
    image.save(filename)

def generate_sprite_from_frames(framesPath, columns, size, output):
    framesMap = sorted(glob(framesPath + "*.png"))

    images = []
    for filename in framesMap:
        images.append(imageio.imread(filename))
    imageio.mimsave(output, images,duration=0.2)

    # finalImage.save(output, transparency=0)
    shutil.rmtree(TMP_FRAMES_PATH, ignore_errors=True)
    print "Saved!"

def get_output_prefix():
    if not os.path.exists(TMP_FRAMES_PATH):
        os.makedirs(TMP_FRAMES_PATH)
    return TMP_FRAMES_PATH + ("%032x_" % random.getrandbits(128))

def generate_static_thumbnail(video, output):
    #ffmpeg -i vid -vf "select=gt(scene\,0.1),scale=280:-1" -frames:v 1 vid.jpg
    # print subprocess.call(["ls", "-l"])
    subprocess.call(["ffmpeg", "-i", video,"-ss","18","-vf","select=gt(scene\,0.01),scale=280:-1","-frames:v","1",output])

def sqlite_insert(conn, table, row):
    cols = ', '.join('"{}"'.format(col) for col in row.keys())
    vals = ', '.join(':{}'.format(col) for col in row.keys())
    sql = 'INSERT INTO "{0}" ({1}) VALUES ({2})'.format(table, cols, vals)
    conn.cursor().execute(sql, row)
    conn.commit()

def updateDB(f):
    # print 'f = ', f
    try:
        thumb001 = os.path.basename(f)
        subdir = os.path.split(os.path.dirname(f))[1]
        thumb = thumb001.replace('001.jpg','.jpg')
        thumbfile = os.path.dirname(f)+'/'+thumb
        date, model, setname = subdir.split(' - ')
        year,monthinteger,day = date.split('-')
        month = datetime.date(1900, int(monthinteger), 1).strftime('%B').lower()[0:3]
        if not os.path.isfile(thumbfile):
            print thumbfile
            url = 'https://www.mplstudios.com/updates/'+year+'/'+month+'/'+thumb
            print url
            downloadfile(url,thumbfile)
            print os.path.isfile(thumbfile)
        # else:
        #     pass
        date, model, setname = subdir.split(' - ')
        dir = '/mpl/'+subdir+'/'
        thumb = subdir+'/'+os.path.basename(f).replace('001.jpg','.jpg')
        date = ''.join(date.split('-'))
        sqlite_insert(conn, 'sets', {'model': model, 'thumb': thumb, 'directory': dir, 'date': date, 'photographer': '', 'rating': 0, 'video': 0, 'setname': setname})
    except:
        print subdir
        # splitvals = subdir.split(' - ')
        # date = splitvals[0]
        # model = splitvals[1]
        # setname = ' - '.join(splitvals[2:-1])

def updateDB_video(f):
    # if not os.path.isfile(f+'.jpg'):
    #     generate_static_thumbnail(f, f+'.jpg')
    # if os.path.isfile(f+'.jpg'):
    try:
        thumbfull = os.path.basename(f)
        subdir = os.path.split(os.path.dirname(f))[1]
        try:
            thumb = re.search('(\d\d\d\dv\d)', thumbfull, flags=re.IGNORECASE).group(0)+'a.jpg'
        except:
            thumb = re.search('(\d\d\d\dv)', thumbfull, flags=re.IGNORECASE).group(0)+'a.jpg'
        print subdir+'\t'+thumb
        # exit()
        thumbfile = os.path.dirname(f)+'/'+thumb
        date, model, setname = subdir.split(' - ')
        year,monthinteger,day = date.split('-')
        month = datetime.date(1900, int(monthinteger), 1).strftime('%B').lower()[0:3]
        if not os.path.isfile(thumbfile):
            print thumbfile
            url = 'https://www.mplstudios.com/updates/'+year+'/'+month+'/'+thumb
            print url
            try:
                downloadfile(url,thumbfile)
            except:
                try:
                    downloadfile(url.replace('a.jpg','.jpg'),thumbfile)
                except:
                    pass
            print os.path.isfile(thumbfile)
        # else:
        #     pass
        date, model, setname = subdir.split(' - ')
        dir = '/mpl/'+subdir+'/'+os.path.basename(f)
        thumb = subdir+'/'+thumb
        date = ''.join(date.split('-'))
        try:
            result = sqlite_insert(conn, 'sets', {'model': model, 'thumb': thumb, 'directory': dir, 'date': date, 'photographer': '', 'rating': 0, 'video': 1, 'setname': setname})
        except:
            print "failed"
            print model
        generate_video_thumbnail(f)
    except:
        pass

conn = sqlite3.connect('mpl.db')
setsdb = conn.cursor()
conn.execute('delete from sets')

files = []
start_dir = r'Z:\MPL'

patterns   = ["*.mp4","*.avi","*.wmv"]

for dir,_,_ in os.walk(start_dir):
    for p in patterns:
        for f in glob(os.path.join(dir,p)):
            updateDB_video(f)

pattern   = "[0-9][0-9][0-9][0-9]001.jpg"

for dir,_,_ in os.walk(start_dir):
    for f in glob(os.path.join(dir,pattern)):
        updateDB(f)

# print files
#
