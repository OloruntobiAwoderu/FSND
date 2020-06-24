import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from config import database_credentials


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            database_credentials['username'], database_credentials['password'], 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Test for Category end points
    
    

    def test_get_all_categories(self): 
        res = self.client().get('/categories')
        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(len(data['categories']) > 0)
    

    
     
            
           

    
    def test_error_405_get_all_categories(self):
        """Test wrong method to GET all categories """
        res = self.client().put('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], "Method Not allowed")
        self.assertEqual(data['success'], False)

    #Test create Questions endpoints
    def test_endpoint_not_available(self):
        res = self.client().get('/question')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found')
    
    def test_create_question(self):
        json_create_question = {
            'question' : 'Is this a test question?',
            'answer' : 'Yes it is!',
            'category' : '1',
            'difficulty' : 1
        } 

        res = self.client().post('/questions', json = json_create_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['total_questions'] > 0)
    

    def test_error_create_question(self):
        json_create_question = {
            'question' : 'who is there?',
            'answer' : 'me!',
            'difficulty' : 1
        } 

        res = self.client().post('/questions', json = json_create_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Category can not be blank')
    

    #Test search Questions endpoints
    def test_search_question(self):

        json_search_question = {
            'searchTerm' : 'is',
        } 

        res = self.client().post('/questions/search', json = json_search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)
    
    def test_error_404_search_question(self):
        json_search_question = {
            'searchTerm' : '2010',
        } 

        res = self.client().post('/questions/search', json = json_search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    
    #Test get paginated questions endpoint
    def test_error_405_get_all_questions_paginated(self):
        res = self.client().patch('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], "Method Not allowed")
        self.assertEqual(data['success'], False)

    def test_error_404_get_all_questions_paginated(self):
        res = self.client().get('/questions?page=4005')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "not found")
        self.assertEqual(data['success'], False)
    
    def test_get_all_questions_paginated(self):
        res = self.client().get('/questions?page=1', json={'category:' : 'science'})
        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'] > 0)

    
    #Test delete questions endpoint
    def test_delete_question(self):
        create_question = {
            'question' : 'Who is the besr player in the world?',
            'answer' : 'Lionel Messi',
            'category' : '1',
            'difficulty' : 1
        } 

        res = self.client().post('/questions', json = create_question)
        data = json.loads(res.data)
        question_id = data['created'] 

       
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], question_id)
    
    def test_404_delete_question(self):
        res = self.client().delete('/questions/{}'.format(900))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Question with id {} does not exist.'.format(900))
    

    #Tests for get questions by category
    def test_400_get_questions_from_category(self):
        res = self.client().get('/categories/900/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'No questions with category 900 found.')
    
    def test_get_questions_from_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)
        self.assertEqual(data['current_category'], 1)

    #Test for posting quizzes
    def test_error_405_play_quiz(self):
        res = self.client().get('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method Not allowed')

    def test_error_400_play_quiz(self):
        
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Please provide a JSON body with previous question Id\'s and optional category.')

    def test_play_quiz_with_category(self):
        play_quizz = {
            'previous_questions' : [1, 2, 5],
            'quiz_category' : {
                'type' : 'Science',
                'id' : '1'
                }
        } 
        res = self.client().post('/quizzes', json = play_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question']['question'])
        self.assertTrue(data['question']['id'] not in play_quizz['previous_questions'])



    

    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
