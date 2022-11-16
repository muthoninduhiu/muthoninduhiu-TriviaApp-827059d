import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category,db
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = os.getenv("DB_TEST_NAME")
        self.database_user = os.getenv("DB_USER")
        self.database_password = os.getenv("DB_PASSWORD")
        self.database_path = "postgresql+psycopg2://{}:{}@{}/{}".format(
                            self.database_user, self.database_password, "localhost:5432", self.database_name)
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
    """
        In this method we check whether the catgeries route works 
        as desired and returns a dictionary of id and type items
        this test should pass.
    """
    def test_retrieve_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['categories']))

    """
        In this method we check whether the questions route works 
        as desired and returns a list of questions. 
        this test should pass.
    """
    def test_retrieve_questions(self):#should pass
        res = self.client().get('/questions')
        data = json.loads(res.data)
        categories = Category.query.order_by(Category.id).all()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
    """
        In this method the request questions route is beyond 
        what is available and returns a list of questions. 
        this test should fail as it is beyond our scope.
    """
    def test_retrieve_questions_beyond_valid_page(self):#should fail
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    """
        In this method we check whether we can delete a question
        given an id.  
        this test should pass.
    """
    def test_delete_question(self): 
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 5).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'],5)
        self.assertEqual(question, None)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
    
    """
        In this method we check whether we can delete a question
        given an id.But this is not an existing question so
        this test should fail.
    """
    def test_delete_question_does_not_exist(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 100).one_or_none()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'Unproccesable')
    
    """
        In this method we check whether we can create a new question.
        This should pass and add the new question to the questions
        this test should pass.
    """
    def test_post_question(self):
        res = self.client().post('/questions',json = {
                                                'question': 'New question',
                                                'answer': 'New answer',
                                                'category': 2,
                                                'difficulty': 1
                                            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))
    """
        In this method we check whether we can search for a question 
        with a given term. This should pass and return the questions 
        with seach term,their total,and success message.
        this test should pass.
    """
    def test_search_question(self):
        res = self.client().post('/questions/search',json = {'searchTerm': 'what is'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'],2)
        self.assertTrue(len(data['questions']))
    """
        In this method we check whether we can search for a question 
        with a given term. This should pass and return the questions 
        with seach term,their total,and success message. The questions 
        here are an empty list because no question matches this term.
        this test should pass.
    """
    def test_search_question_not_found_with_success(self):
        res = self.client().post('/questions/search',json = {'searchTerm': 'udacity'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'],0)
        self.assertEqual(len(data['questions']),0)

    """
        In this method we check whether we can search for a question 
        with a given term. This should fail because there is nothing to 
        search for this test should fail.
    """
    def test_search_question_not_found_without_success(self):
        res = self.client().post('/questions/search',json = {'searchTerm': ''})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(len(data['message']),'bad request')

    """
        In this method we check whether we can search for a question 
        via the categories. This should pass and return the total questions 
        in category,current category,and success message.
        this test should pass.
    """
    def test_get_question_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 4)
        self.assertEqual(data['current_category'], 2)
    
    """
        In this method we check whether we can search for a question 
        via the categories. This should pass and return the total questions 
        in category,current category,and success message. Except the current 
        category will be 100, the questions an empty array,total questions zero 
        and a success message  this test should pass.
    """
    def test_get_question_by_category_without_any_questions(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)
    """
        In this method we check whether we can search for a question 
        via the categories. This should fail and return success message.
        this test should fail.
    """
    def test_get_question_by_category_with_error(self):
        res = self.client().get('/categories/2000000000000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    
        

    

        



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()