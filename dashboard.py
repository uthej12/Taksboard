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

class dashboard(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "text/html"

        user =users.get_current_user()

        template_values = {
            'user':False,
            'login': '',
            'logout': '',
            'name':'',
            'boards':[]
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
                'boards':boards
            }
        else:
            login_url = users.create_login_url('/')
            template_values = {
                'user': False,
                'login': login_url,
                'logout': '',
                'name':'',
                'boards':[]
            }
    
        template = JINJA_ENVIRONMENT.get_template('dashboard.html')
        self.response.write(template.render(template_values))
    
    def post(self):

        title = self.request.get('title')

        new_board = TaskBoard()
        new_board.title = title

        user_name = users.get_current_user().nickname()
        current_user = ndb.Key(User, user_name)
        
        new_board.owner = current_user.get()
        new_board.users.append(current_user.get())
        new_board_key = new_board.put()

        if current_user.get().boards == None:
            current_user.get().boards = []
            current_user.get().boards.append(new_board_key.urlsafe())
            current_user.get().put()
        else:
            current_user.get().boards.append(new_board_key.urlsafe())
            current_user.get().put()

        self.redirect('/dashboard')