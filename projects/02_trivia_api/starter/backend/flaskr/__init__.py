import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-control-Allow-Headers',
                             'content-Type, Authorization, true')
        response.headers.add('Access-control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')
        return response

#----------------------------------------------------------------------------#
# Custom Built Functions
#----------------------------------------------------------------------------#

    def pagination(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    def customErrorMessages(error, default_message):
        try:
            return error.description['message']
        except TypeError:
            return default_message

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories', methods=['GET'])
    def get_all_categories():

        categories = Category.query.all()

        if not categories:

            abort(404)

        all_categories = [category.format() for category in categories]

        returned_categories = []
        for index in all_categories:
            returned_categories.append(index['type'])

        return jsonify({
            "success": True,
            "status code": 200,
            "categories": returned_categories
        })

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions', methods=['GET'])
    def get_questions():

        selection = Question.query.order_by(Question.id).all()
        paginated_questions = pagination(request, selection)
        if len(paginated_questions) == 0:
            abort(404)
        categories = Category.query.all()
        all_categories = [category.format() for category in categories]

        returned_categories = []
        for cat in all_categories:
            returned_categories.append(cat['type'])
        return jsonify({
            "success": True,
            "questions": paginated_questions,
            "total_questions": len(selection),
            "categories": returned_categories,
            "current_category": returned_categories
        })

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        if not question:
            abort(
                404, {'message': 'Question with id {} does not exist.'.format(question_id)})

        question.delete()
        return jsonify({
            "success": True,
            "deleted": question_id,
        })

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @ app.route('/questions', methods=['POST'])
    def create_questions():
        body = request.get_json()

        if not body:
            abort(400, {'message': 'request does not contain a valid JSON body.'})

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        if not new_question:
            abort(400, {'message': 'Question can not be blank'})

        if not new_answer:
            abort(400, {'message': 'Answer can not be blank'})

        if not new_category:
            abort(400, {'message': 'Category can not be blank'})

        if not new_difficulty:
            abort(400, {'message': 'Difficulty can not be blank'})
        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )
            question.insert()

            selections = Question.query.order_by(Question.id).all()
            questions_paginated = pagination(request, selections)

            return jsonify(
                {
                    "success": True,
                    'created': question.id,
                    "questions": questions_paginated,
                    "total_questions": len(selections)
                }
            )
        except:
            abort(422)
    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @ app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()

        search_term = body.get('searchTerm', None)

        if search_term:
            questions = Question.query.filter(
                Question.question.contains(search_term)).all()
            if not questions:
                abort(
                    404, {'message': 'questions that contains "{}" not found.'.format(search_term)})

            question_found = [question.format() for question in questions]
            selections = Question.query.order_by(Question.id).all()

            categories = Category.query.all()
            all_categories = [category.format() for category in categories]

            return jsonify({
                "success": True,
                "questions": question_found,
                "total_questions": len(selections),
                "current_category": all_categories
            })

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @ app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_categories(category_id):

        selection = (Question.query.filter(Question.category == str(
            category_id)).order_by(Question.id).all())

        if not selection:
            abort(
                404, {'message': 'No questions with category {} found.'.format(category_id)})

        questions_paginated = pagination(request, selection)

        if not questions_paginated:
            abort(404, {'message': 'No questions in the sslected page.'})

        return jsonify({
            "success": True,
            "questions": questions_paginated,
            "total_questions": len(selection),
            "current_category": category_id
        })

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @ app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        if not body:
            abort(400, {
                  'message': 'Please provide a JSON body with previous question Id\'s and optional category.'})

        previous_questions = body.get('previous_questions', None)
        current_category = body.get('quiz_category', None)

        if not previous_questions:
            if current_category:
                raw_questions = Question.query.filter(
                    Question.category == str(current_category['id'])).all()
            else:
                raw_questions = Question.query.all()
        else:
            if current_category:
                raw_questions = (Question.query.filter(Question.category == str(current_category['id']))
                                 .filter(Question.id.notin_(previous_questions))
                                 .all())
            else:
                raw_questions = (Question.query.filter(Question.id.notin_(previous_questions))
                                 .all())
        formatted_questions = [question.format() for question in raw_questions]
        random_question = formatted_questions[random.randint(
            0, len(formatted_questions))]

        return jsonify({
            "success": True,
            "question": random_question
        })


        '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @ app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": customErrorMessages(error, 'bad request')

        }), 400

    @ app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": customErrorMessages(error, 'not found')

        }), 404

    @ app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": customErrorMessages(error, 'unproccessable')

        }), 422

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method Not allowed'
        }), 405

    return app
