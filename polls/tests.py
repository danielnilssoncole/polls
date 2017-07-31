import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question, Choice

#to do
# update create question function to create questions with choices so
# tests will pass is null tests

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days, choice_text):
    time = timezone.now() + datetime.timedelta(days=days)
    q = Question(question_text=question_text, pub_date=time)
    q.save()
    q.choice_set.create(choice_text=choice_text, votes=0)
    # return Question.objects.create(question_text=question_text, pub_date=time)
    return q

def create_question_no_choice(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        create_question(question_text='Past question.', days=-30, choice_text='past choice')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        create_question(question_text='Future question.', days=30, choice_text='future choice')
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        create_question(question_text='Past question.', days=-30, choice_text='past choice')
        create_question(question_text='Future question.', days=30, choice_text='future choice')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        create_question(question_text='Past question 1.', days=-30, choice_text='past choice q1')
        create_question(question_text='Past question 2.', days=-5, choice_text='past choice q2')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

    def test_no_choice_and_choice(self):
        create_question(question_text='With choice question', days=-30, choice_text='choice')
        create_question_no_choice(question_text='No choice question 2.', days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: With choice question>']
        )

class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        future_question = create_question(question_text='Future question.', days=30, choice_text='future choice')
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text='Past question.', days=-30, choice_text='past choice')
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)

    def test_no_choice(self):
        no_choice_question = create_question_no_choice(question_text='No choice question.', days=-5)
        url = reverse('polls:detail', args=(no_choice_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class QuestionResultsViewTests(TestCase):

    def test_future_question(self):
        future_question = create_question(question_text='Future question.', days=30, choice_text='future choice')
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text='Past question.', days=-30, choice_text='past choice')
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)

    def test_no_choice(self):
        no_choice_question = create_question_no_choice(question_text='No choice question.', days=-5)
        url = reverse('polls:results', args=(no_choice_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
