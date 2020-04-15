import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb

from Models import TaskBoard
from Models import Task
from Models import User


JINJA_ENVIRONMENT = jinja2.Environment(
loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
extensions = ['jinja2.ext.autoescape'],
autoescape = True)

class taskBoard(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "text/html"

        taskBoard = self.request.get('key')
        taskBoard = ndb.Key(urlsafe = taskBoard).get()
        #self.response.write(key)

        user =users.get_current_user()

        template_values = {
            'user':False,
            'login': '',
            'logout': '',
            'name':'',
            'Data':taskBoard
        }

        if user:
            nickname = user.nickname()

            key = ndb.Key(User, nickname)
            if key.get() == None:
                new = User(id=nickname,email=nickname)
                new.put()

            boards = []
            if key.get().boards != None:
                for board in key.get().boards:
                    boards.append(ndb.Key(urlsafe = board))
                #self.response.write(boards)
            
            logout_url = users.create_logout_url('/')
            template_values = {
                'user': True,
                'login':'',
                'logout': logout_url,
                'name':nickname,
                'Data': taskBoard
            }
        else:
            login_url = users.create_login_url('/')
            template_values = {
                'user': False,
                'login': login_url,
                'logout': '',
                'name':'',
                'Data':taskBoard
            }
    
        template = JINJA_ENVIRONMENT.get_template('taskBoard.html')
        self.response.write(template.render(template_values))