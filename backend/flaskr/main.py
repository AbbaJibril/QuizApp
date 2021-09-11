import os
import random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS 
from models import setup_db, Question, Category
# for generic exception handling
from werkzeug.exceptions import HTTPException



questionsPerPage = 10
def paginateQuestions(request,selection):
  currentQuestions = []
  page = request.args.get('page', 1 , type = int)
  start = (page-1)*questionsPerPage 
  end = start + questionsPerPage
  questions = [question.format() for question in selection]
  currentQuestions = questions[start:end]
  return currentQuestions

def getCategoriesDict(categories):
  #returns a dictionary of {id:type} for all categories
  categoriesDict={}
  for category in categories:
    categoriesDict[category.id] = category.type
  return(categoriesDict)

def CreateApp (test_config = None):
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources = {r"/*": {"origins": "*"}})

  #CORS Headers
  @app.after_request
  def after_request (response):
    response.header.add('Access-Control_Allow-Headers', 'Content-Type, Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
    return response

  
  @app.route('/', methods = ['GET'])
  #endpoint for API's root
  def index():
    try:
      questions = [question.format()
      for question in Questions.query.order_by(Question.id).all()]
      categories = Category.query.order_by(Category.id).all()
      return jsonify({
        'success': True,
        'categories': getCategoriesDict(categories),
        'totalCategories': len(categories),
        'questions': questions,
        'totalQuestions': len(questions)
         })
    except:
      abort(500)

  #endpoint to handle GET requests for all categories.
  @app.route('/categories', methods = ['GET'])
  def getCategories():
    categories = Category.query.order_by(Category.id).all()
    if(len(categories)==0):
      abort(404)
    return jsonify({
      'success': True,
      'categories':getCategoriesDict(categories)
      })

  #endpoint to create a new category
  @app.route('/categories', methods = ['POST'])
  def createCategories():
    try:
      body = request.get_json()
      categoryType = body.get('type', None)
      if(categoryType is None):
        abort(422)
      category = Category(type = categoryType)
      category.insert()
      selection = Category.query.order_by(Category.id).all()

      return jsonify({
        'success': True,
        'created': category.id,
        'totalCategories': len(selection)
        })
    except: 
      abort(422)

  #endpoint to delete a category
  @app.route('/categories/<int:category_id>', methods = ['DELETE'])
  def deleteCategory(category_id):
    try:
      category = Category.query.get(category_id)
      if category is None:
        abort(404)
      category.delete()
      selection = Category.query.order_by(Category.id).all()
      return jsonify({
        'success': True,
        'deleted': category.id,
        'totalCategories':len(selection)
        })
    except:
      abort(422)


  #endpoint to handle GET requests for questions
  @app.route('/questions', methods=['GET'])
  def getQuestions():
    selection = Question.query.order_by(Question.id).all()
    currentQuestions = paginateQuestions(request, selection)
    if(len(currentQuestions)==0):
      abort(404)
    categories = Category.query.order_by(Category.id).all()
    return jsonify({
      'success' : True,
      'questions' : currentQuestions,
      'totalQuestions' : len(selection),
      'categories' : getCategoriesDict(categories),
      })

  #endpoint to DELETE question using a question ID
  @app.route('/questions/<int:question_id', methods = ['DELETE'])
  def deleteQuestion(question_id):
    try:
      question = Question.query.get(question-id)
      if question is None:
        abort(404)
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      return jsonify({
        'success' : True,
        'deleted' : question_id,
        'totalQuestions' : len(selection)
       })
    except:
      abort(422)

  #endpoint to POST a new question
  @app.route('/questions', methods = ['POST'])
  def createSearchQuestions():
    body = request.get_json()
    question = body.get('question', None)
    answer = body.get('answer', None)
    category = body.get('category', None)
    difficultyLevel = body.get('difficultyLevel', None)
    search = body.get('searchTerm', None)

    try:
      if search is not None:
        if(len(search) == 0):
          selection = Question.query.order_by(Question.id).all()
        else:
          selection = Question.query.order_by(Question.id).filter(Questions.questions.ilike('%{}%'.format(search))).all()

        currentQuestions = paginateQuestions(request, selection)
        return jsonify({
          'success' : True,
          'questions' : currentQuestions,
          'totalQuestions' : len(selection)
          })

      else:
        if(not(question and answer and category and difficultyLevel)):
          abort(422)
        question_obj = Question(question = question, answer = answer, category = category, difficultyLevel = difficultyLevel)
        question_obj.insert()
        selection = Question.query.order_by(Question.id).all()
        currentQuestions = paginateQuestions(request, selection)
        return jsonify({
          'success':True,
          'created': question_obj.id,
          'questions':currentQuestions,
          'totalQuestions' : len(selection)
          })

    except Exception as e:
      abort(422)

  #GET endpoint to get questions based on category
  @app.route('/categories/<int:category_id>/questions',methods=['GET'])
  def getQuestionsByCategory(category_id):
    category = Category.query.get(category_id)
    if category is None :
      abort(404)
    
    selection = Question.query.order_by(Question.id).filter(Question.category == category_id ).all()
    current_questions = paginateQuestions(request, selection)

    return jsonify({
            'success':True,
            'questions':currentQuestions,
            'totalQuestions' : len(selection),
            'currentCategory' : category_id
            })


  #POST endpoint to get questions to play the quiz
  @app.route('/quizzes', methods=['POST'])
  def getQuizQuestion():
    body = request.get_json()
    try:
      previousQuestions = body.get('previousQuestions')
      quizCategory = body.get('quizCategory')['id']
      
      if (previousQuestions is None):
              abort(400)

      questions = []
      if quizCategory == 0 :
        questions = Question.query.filter(Question.id.notin_(previousQuestions)).all()
      else:
        category = Category.query.get(quizCategory)
        if category is None:
          abort(404)
        questions = Question.query.filter(Question.id.notin_(previousQuestions),Question.category == quizCategory).all()
      currentQuestion = None
      if(len(questions)>0):
        index = random.randrange(0, len(questions))
        currentQuestion = questions[index].format()
      return jsonify({
              'success':True,
              'question':currentQuestion,
              'totalQuestions' : len(questions),
              })
    except Exception as e:
      abort(400)

  #error handlers for all expected errors including 404 and 422

  @app.errorhander(HTTPException)
  def handleException(e):
    return jsonify({
      "success": False,
      "error": e.code
      "message": e.name
     }), e.code

  return app