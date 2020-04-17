from google.appengine.ext import ndb

class User(ndb.Model):
    email = ndb.StringProperty()
    boards = ndb.JsonProperty()
class Task(ndb.Model):
    title = ndb.StringProperty()
    due_date = ndb.DateTimeProperty()
    completion_date = ndb.DateTimeProperty()
    status = ndb.StringProperty()
    user = ndb.StructuredProperty(User, repeated = False)
    description = ndb.StringProperty()

class TaskBoard(ndb.Model):
    title = ndb.StringProperty()
    owner = ndb.StructuredProperty(User, repeated = False)
    tasks = ndb.StructuredProperty(Task, repeated = True)
    users = ndb.StructuredProperty(User, repeated = True)
    

