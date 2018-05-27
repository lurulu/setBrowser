import sys, time, os, re, string, sqlite3
from glob import glob
from docopt import docopt
import cv2
from PIL import Image
from click import progressbar
import os, random, shutil, math, tempfile, subprocess, datetime
import imageio

os.environ['PATH'] = os.path.dirname(r'C:\Program Files (x86)\MediaInfo.dll\MediaInfo_InfoTip.dll') + ';' + os.environ['PATH']
from pymediainfo import MediaInfo

TMP_FRAMES_PATH = './joymiiframes/'

def generate_video_thumbnail(video):
    print video
    generate_video_thumbnail_file(video)

def generate_video_thumbnail_file(video):
    videoFileClip = video
    interval = 50
    size = 250, 250
    output = video+'.gif'
    outputPrefix = get_output_prefix()
    print 'output = ', output
    if not os.path.isfile(output):
        generate_frames(videoFileClip, interval, outputPrefix, size)
        generate_sprite_from_frames(outputPrefix, output)

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

def generate_sprite_from_frames(framesPath, output):
    framesMap = sorted(glob(framesPath + "*.png"))

    images = []
    for filename in framesMap:
        images.append(imageio.imread(filename))
    # print 'images = ', images
    # print 'output = ', output
    imageio.mimsave(output, images, duration=0.2)

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
    subprocess.call(["ffmpeg", "-i", video,'-ss','25',"-vf","select=gt(scene\,0.1),scale=280:-1","-frames:v","1",output])

conn = sqlite3.connect('joymii.db')
setsdb = conn.cursor()
conn.execute('delete from sets')

files = []
start_dir = r'Z:\Joymii'
patterns   = ("*.mp4", "*.wmv","*.mov")

def sqlite_insert(conn, table, row):
    cols = ', '.join('"{}"'.format(col) for col in row.keys())
    vals = ', '.join(':{}'.format(col) for col in row.keys())
    sql = 'INSERT INTO "{0}" ({1}) VALUES ({2})'.format(table, cols, vals)
    conn.cursor().execute(sql, row)
    conn.commit()

for dir,_,_ in os.walk(start_dir):
    for pattern in patterns:
        files.extend(glob(os.path.join(dir,pattern)))

print files

for f in files:
    if not os.path.isfile(f+'.jpg'):
        generate_static_thumbnail(f, f+'.jpg')
    if os.path.isfile(f+'.jpg'):
        setname = os.path.basename(f)
        dir = '/joymii/'+setname
        thumb = dir+'.jpg'
        # print os.path.basename(f)
        date = re.search('(\d\d\.\d\d\.\d\d)', setname, flags=re.IGNORECASE).group(0)
        y, m, d = string.split(date,'.')
        date = '20'+y+m+d
        # print date
        try:
            model = string.split(setname,'-')[1]#.replace('-&-','.and.').replace('.','-')
        except:
            # pass
            # model = string.split(re.search('(\d\d\.\d\d\.\d\d)\.(.*)', setname, flags=re.IGNORECASE).group(2),'-')[0]
            print setname
        try:
            setname = string.capwords(string.split(dir,'-')[2].replace('.mp4','').replace('.',' '))
        except:
             print dir
             exit()
        sqlite_insert(conn, 'sets', {'model': model, 'thumb': thumb, 'directory': dir, 'date': date, 'photographer': '', 'rating': 0, 'video': 1, 'setname': setname})
        generate_video_thumbnail(f)
