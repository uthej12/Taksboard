import webapp2
import jinja2
import os
import datetime
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
            'Data':taskBoard,
            'Error': '',
            'Success':''
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

        if len(self.request.get('error')) > 1:
            template_values['Error'] = self.request.get('error')

        if len(self.request.get('success')) > 1:
            template_values['Success'] = self.request.get('success')
    
        template = JINJA_ENVIRONMENT.get_template('taskBoard.html')
        self.response.write(template.render(template_values))
    def post(self):
        
        button = self.request.get('perform_action')

        if button == 'Add':
            board = ndb.Key(urlsafe=self.request.get('key'))
            #self.response.write(board.get())

            title = self.request.get('title').lower()
            date = self.request.get('dueDate')
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            description = self.request.get('description')
            user = ndb.Key(User, self.request.get('user')).get()
            task_key = ndb.Key(Task, title)
            
            if task_key.get() == None:
                new_task = Task(id=title)
                new_task.title = title
                new_task.due_date = date
                new_task.status = 'False'
                new_task.description = description
                new_task.user = user
                new_key = new_task.put()

                board = board.get()
                board.tasks.append(new_key.get())
                board_key = board.put()
                self.redirect('/taskBoard?key='+self.request.get('key')+'&success=Task created successfully')
            else:
                self.redirect('/taskBoard?key='+self.request.get('key')+'&error=Task with same name exists')
        if button =='invite':
            email = self.request.get('invite_user')
            board = ndb.Key(urlsafe=self.request.get('key'))

            key = ndb.Key(User, email)
            
            if key.get() == None:
                self.redirect('/taskBoard?key='+self.request.get('key')+'&error=No user with the given email present')
            else:
                user = key.get()

                if user.boards == None:
                    user.boards = []
                if board.urlsafe() not in user.boards:
                    user.boards.append(board.urlsafe())
                    new_key = user.put()
                    board_current =board.get()
                    board_current.users.append(new_key.get())
                    board_current.put()
                    self.redirect('/taskBoard?key='+self.request.get('key')+'&success=Successfully added '+user.email+' to Board')
                else:
                    self.redirect('/taskBoard?key='+self.request.get('key')+'&error=User already present in taskboard')
                