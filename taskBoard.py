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
            'Success':'',
            'Edit':None
        }

        #Handel Status Change
        if len(self.request.get('change-status')) > 0:
            task_key =self.request.get('change-status')+'|'+taskBoard.key.urlsafe()
            task_key = ndb.Key(Task, task_key)
            task = task_key.get()

            if task.status == 'False':
                task.status = 'True'
                task.completion_date = datetime.datetime.now()
            elif task.status == 'True':
                task.status = 'False'
                task.completion_date = None

            for t in taskBoard.tasks:
                if t.title == self.request.get('change-status'):
                    if t.status == 'False':
                        t.status = 'True'
                        t.completion_date = datetime.datetime.now()
                    elif t.status == 'True':
                        t.status = 'False'
                        t.completion_date = None
            task.put()
            board_key = taskBoard.put()
            self.redirect('/taskBoard?key='+board_key.urlsafe()+"&success=Changed status successfully")
        
        #Handel delete requets
        if len(self.request.get('delete-task')) > 0:
            task_key =self.request.get('delete-task')+'|'+taskBoard.key.urlsafe()
            task_key = ndb.Key(Task, task_key)
            task = task_key.get()
            
            for t in taskBoard.tasks:
                if t.title == task.title:
                    taskBoard.tasks.remove(t)
            task_key.delete()
            board_key = taskBoard.put()
            self.redirect('/taskBoard?key='+board_key.urlsafe()+"&success=Task Deleted successfully")

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

        if len(self.request.get('edit-task')) > 0:
            task_key =self.request.get('edit-task')+'|'+taskBoard.key.urlsafe()
            task_key = ndb.Key(Task, task_key)
            task = task_key.get()
            template_values['Edit'] = task
            #self.response.write(template_values)
        else:
            template_values['Edit'] = None

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
            
            task_key =title+'|'+board.urlsafe()
            task_key = ndb.Key(Task, task_key)
            
            if task_key.get() == None:
                new_task = Task(id=str(title+'|'+board.urlsafe()))
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


        if button == 'editTask':
            board = ndb.Key(urlsafe=self.request.get('key'))
            #self.response.write(board.get())

            title = self.request.get('title')
            #self.response.write(title)
            date = self.request.get('dueDate')
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            #self.response.write(date)
            description = self.request.get('description')
            #self.response.write(description)
            assigned = self.request.get('assigned')
            #self.response.write(assigned)
            status = self.request.get('status')
            self.response.write(status)

            user = ndb.Key(User, assigned).get()
            task_key =title+'|'+board.urlsafe()
            task_key = ndb.Key(Task, task_key)
            
            if task_key.get() == None:
                self.redirect('/taskBoard?key='+self.request.get('key')+'&error=Sorry some error occured')
                
            else:
                task = task_key.get()
                task.due_date = date
                self.response.write(task.status)
                self.response.write(len(status))
                if len(status) > 1:
                    if task.status == 'True':
                        pass
                    else:
                        self.response.write('yes')
                        task.status = 'True'
                        task.completion_date = datetime.datetime.now()
                else:
                    if task.status == 'False':
                        pass
                    else:
                        task.status = 'False'
                        task.completion_date = None

                task.description = description
                task.user = user
                task.put()

                board = board.get()
                for t in board.tasks:
                    if t.title == task.title:
                        t.due_date = date
                        if len(status) > 1:
                            if t.status == 'True':
                                pass
                            else:
                                t.status = 'True'
                                t.completion_date = datetime.datetime.now()
                        else:
                            if t.status == 'False':
                                pass
                            else:
                                t.status = 'False'
                                t.completion_date = None

                        t.description = description
                        t.user = user
                board.put()
                        
                board_key = board.put()
                self.redirect('/taskBoard?key='+self.request.get('key')+'&success=Task Edited Successfully')

            
        if button == 'editBoard':
            board = ndb.Key(urlsafe=self.request.get('key'))
            name = self.request.get('taskboardName')
            board = board.get()
            if name == board.title:
                self.redirect('/taskBoard?key='+board_key.urlsafe())
            else:
                board.title = name
                board_key  = board.put()       
                self.redirect('/taskBoard?key='+board_key.urlsafe()+'&success=TaskBoard Name changed successfully')

        if button == 'editUsers':
            board_key = ndb.Key(urlsafe=self.request.get('key'))
            name = self.request.get('user')
            user_key = ndb.Key(User, name)
            user = user_key.get()
            board = board_key.get()

            for u in board.users:
                if u.email == user.email:
                    board.users.remove(u)
            if board_key.urlsafe() in user.boards:
                user.boards.remove(board_key.urlsafe())
            user.put()
            for task in board.tasks:
                if task.user.email == user.email:
                    name = task.title+'|'+(board.key.urlsafe())
                    t = ndb.Key(Task, name).get()
                    t.user = None
                    task.user = None
                    t.put()
            board.put()
            self.redirect('/taskBoard?key='+board_key.urlsafe()+'&success= '+user.email+' Successfully removed from '+board.title)
            