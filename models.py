import os
from sqlalchemy import create_engine, Column, String, Interger
from flask_sqlalchemy import sqlalchemy
import json

databaseName = "quizapp"
databasePath = "postgres://postgres:postgres@{}/{}".format('localhost:5432', databaseName)

db = SQlAlchemy()

def setup_db(app, databasePath = databasePath):
  #binds flask app and SQLAlchemy service
  app.config["SQLALCHEMY_DATABASE_URI"] = databasePath
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
  db.app = app
  db.init_app(app)
  db.create_all()

#Question
#--------------------------------------------------
 
 class Question(db.model):
   __tablename__ = 'questions'
   id = Column(Interger, primary_key = True)
   question = Column(String)
   answer = Column(String)
   category = Column(String)
   difficultyLevel = Column(Integer)

  def __init__(self, question, answer, category, difficultyLevel):
     self.question = question
     self.answer = answer
     self.category = category
     self.difficultyLevel = difficultyLevel

  def insert(self):
    db.session.add(self)
    db.session.commit()

  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'question': self.question,
      'answer': self.answer,
      'category': self.category,
      'difficultyLevel': self.difficultyLevel
    }

#Category
#--------------------------------------------------
class Category(db.Model):  
  __tablename__ = 'categories'

  id = Column(Integer, primary_key = True)
  type = Column(String)

  def __init__(self, type):
    self.type = type
  
  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'type': self.type
    }

