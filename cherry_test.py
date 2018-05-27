import random
import string
import sys, time, os, glob
import pymysql.cursors
import urllib
from random import shuffle
import sqlite3
import cherrypy, mimetypes
from cherrypy.lib.static import serve_file

class database_link(object):

    def __init__(self):
        super(database_link, self).__init__()
        self.chosenSite = "wowporn"
        self.application_path = '.\\'

    def initialise_db_connection(self):
        self.connection = sqlite3.connect(self.application_path+self.chosenSite+'.db')
        self.sets = self.connection.cursor()
        self.conn = sqlite3.connect(self.application_path+'thumbs_'+self.chosenSite+'.db')
        self.thumbshelf = self.conn.cursor()

    def getData(self, model=None):
        self.model=model
        sql = "SELECT * FROM `sets` where `date` > 0 "
        if self.model is not None:
            if len(list(self.model.split("-&-"))) > 1:
                models = list(self.model.split("-&-"))
                for model in models:
                    if model == models[0]:
                        sql = sql + "AND `model` LIKE \"%"+str(model)+"%\" "
                    else:
                        sql = sql + "OR `model` LIKE \"%"+str(model)+"%\" "
            else:
                sql = sql + "AND `model` LIKE \"%"+str(self.model)+"%\" "
        sql = sql + "ORDER BY -date "
        sql = sql + ";"
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.result = cursor.fetchall()
        print len(self.result)
        return self.result

class StringGenerator(object):

    def __init__(self):
        self.database = database_link()

    @cherrypy.expose
    def index(self, offset=0, model=None, returning=False):
        if returning:
            offset = cherrypy.session['offset']
        else:
            offset = int(offset)
        offset = 0 if offset < 0 else offset
        self.database.initialise_db_connection()
        self.result = self.database.getData(model=model)[offset:offset+(6*4)]
        i = 0
        html = '''<!DOCTYPE html>
        <html class=''>
    <head><style>
body {
    background-color: black;
    color: white;
}
</style></head>
    <body><table width="100%" height="100%">
        <tr height="20px"><td style="width:26px"><a href="?offset='''+str(offset-(6*4)-1)+'''"><img src="/static/prev.gif" alt="Previous"/></a></td>'''
        if model is not None:
            html+='<td><a href="?returning=True">Return</a></td>'
        else:
            cherrypy.session['offset'] = offset
        html+='''<td colspan=4 style="width:100%"></td>
        <td style="width:26px;" align="right"><a href="?offset='''+str(offset+(6*4)+1)+'''"><img src="/static/next.gif" alt="Next"/></a></td>
        </tr>
        <tr>'''
        for models, thumb, location, date, photographer, something, video, setname in self.result:
            i += 1
            html += '''<td><table><tr><td colspan="2">
            <a href="/video?location='''+location+'''"><img src="'''+thumb+'''"></a></td></tr>
            <tr><td>'''+setname+'''</td>'''
            # models = ' '.join(models.split('.')).split(' and ')
            if len(models.split('.and.')) > 1:
                html+='''<td><table>'''
                for m in models.split('.and.'):
                    html+='''<tr><td><a href="?model='''+str(m)+'''">'''+str(m)+'''</a></td></tr>'''
                html+='''</table>'''
            else:
                html+='''<td><a href="?model='''+str(models)+'''">'''+str(models)+'''</a></td>'''
            html+='''</tr></table></td>'''
            if i > 5:
                html += '''</tr><tr>'''
                i = 0
        html += '''</tr></table></body></html>'''
        return html

    @cherrypy.expose
    def video(self, location):
        videofile = os.path.basename(location)
        BASE_PATH = '\\\\192.168.0.5\\iSCSI\\wowporn\\'
        video = os.path.join(BASE_PATH, videofile)
        if video == None:
            return "no file specified!"
        if not os.path.exists(video):
            return "file not found!"

        mime = mimetypes.guess_type(video)[0]
        # return '''<video width="320" height="240" controls>
        #     <source src="'''+location+'''" type="'''+mime+'''">
        #     Your browser does not support the video tag.
        # </video>'''

        return '''<!DOCTYPE html><html class=''>
    <head>
  <link href="https://vjs.zencdn.net/4.3/video-js.css" rel="stylesheet">
  <script src="https://vjs.zencdn.net/4.3/video.js"></script>

</style><style>
body {
background-color: black;
color: white;
}
</style></head><body>

  <video id="my_video_1" class="video-js vjs-default-skin" controls preload="none"
  data-setup='{ "autoplay": true }'>
    <source src="'''+location+'''" type="'''+mime+'''">
  </video>
<script >
videojs.autoSetup();

    videojs('my_video_1').ready(function(){
      console.log(this.options()); //log all of the default videojs options

       // Store the video object
      var myPlayer = this, id = myPlayer.id();
      // Make up an aspect ratio
      var aspectRatio = 1080/1920;

      function resizeVideoJS(){
        var width = document.getElementById(id).parentElement.offsetWidth;
        myPlayer.width(window.innerWidth-10).height( window.innerHeight - 30 );
      }

      // Initialize resizeVideoJS()
      resizeVideoJS();
      // Then on resize call resizeVideoJS()
      window.onresize = resizeVideoJS;
      mPlayer.FullscreenToggle();
    });
</script>
</body></html>'''

    @cherrypy.expose
    def videofile(self, video):
        videofile = os.path.basename(video)
        BASE_PATH = '\\\\192.168.0.5\\iSCSI\\wowporn\\'
        videolocation = os.path.join(BASE_PATH, videofile)
        print videolocation
        size = os.path.getsize(videolocation)
        mime = mimetypes.guess_type(videolocation)[0]
        print(mime)
        f = open(videolocation,'rb')
        cherrypy.response.headers["Content-Type"] = mime
        cherrypy.response.headers["Content-Disposition"] = 'attachment; filename="%s"' % os.path.basename(videofile)
        cherrypy.response.headers["Content-Length"] = size

        BUF_SIZE = 1024 * 1

        def stream():
            data = f.read(BUF_SIZE)
            while len(data) > 0:
                yield data
                data = f.read(BUF_SIZE)

        return stream()
    videofile._cp_config = {'response.stream': True}

if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'tools.sessions.on': True,
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'C:\\Users\\james\\Documents\\python\\setBrowser\\static'
        },
        '/wowfiles': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '\\\\192.168.0.5\\iSCSI\\wowporn\\'
        }
    }
    cherrypy.quickstart(StringGenerator(),'/',conf)
