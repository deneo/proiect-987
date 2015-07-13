from __future__ import unicode_literals

import os
import webapp2
import jinja2
import textile
import cgi
import re

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

def blog_key(name = 'default'):
	return db.Key.from_path('blog', name)

class Category(db.Model):
	categorie = db.StringProperty()
	link_poza = db.StringProperty()

class Curs(db.Model):
	titlu = db.StringProperty(required = True)
	continut = db.TextProperty(required = True)
	categorie = db.StringProperty()	

class Question(db.Model):
	_parent = db.StringProperty()
	question = db.StringProperty()
	answer1 = db.StringProperty()
	answer2 = db.StringProperty()
	answer3 = db.StringProperty()
	answer4 = db.StringProperty()
	correctAnswer = db.StringProperty()

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
			self.response.out.write(*a, **kw)

	def render_str(self, template, **param):
		t = jinja_env.get_template(template)
		return t.render(param)

	def render(self, template, **kw):
		courses = db.GqlQuery("SELECT * FROM Curs ORDER BY titlu")
		self.write(self.render_str(template, courses = courses, title = "Platorma de cursuri online", **kw))


class add_course(Handler):
	def render_add_course(self, mesaj="", titlu="", continut="", categorie=""):
		self.render("adauga_curs.html", mesaj = mesaj, titlu = titlu, text = continut, categorie = categorie)

	def get(self, curs_id):
		if curs_id != '':
			key = db.Key.from_path('Curs', int(curs_id), parent = blog_key())

			curs = db.get(key)

			self.render_add_course(titlu = curs.titlu, continut = curs.continut, categorie = curs.categorie)
			curs.delete()
			cursuri = db.GqlQuery("SELECT * FROM Curs WHERE categorie = '%s'" % curs.categorie)
			if cursuri.count() == 1:
				categorie = db.GqlQuery("SELECT * FROM Category WHERE categorie = '%s'" % curs.categorie)
				print categorie.count()
				for cat in categorie:
					cat.delete()
		else:
			self.render_add_course()

	def post(self, curs_id = None):
		titlu = self.request.get("titlu")

		continut = self.request.get("continut")

		categorie = self.request.get("categorie")


		if isinstance(continut, str):
			continut = unicode(continut, 'utf-8')
		else:
		    continut = unicode(continut)

		if titlu and continut:
			cursuri = db.GqlQuery("SELECT * FROM Curs WHERE titlu = '%s'" % titlu)
			mesaj = ""
			for curs in cursuri:
				if curs.titlu == titlu:
					mesaj = "Eroare, exista deja un curs cu acest titlu!"
			if mesaj == "":
				continut = cgi.escape(continut)
				obj = Curs(parent = blog_key(), titlu = titlu, continut = continut, categorie = categorie)
				obj.put()
				categorii = db.GqlQuery("SELECT * FROM Category WHERE categorie = '%s'" % categorie);
				if categorie != '' and categorii.count() == 0:
					obj2 = Category (parent = blog_key(), categorie = categorie)
					obj2.put()

				self.redirect('/curs/%s' % str(obj.key().id()))
			else:
				self.render_add_course(mesaj, titlu = curs.titlu, continut = curs.continut)
		else:
			mesaj = "Eroare, trebuie sa ai neaparat un titlu si continutul"
			self.render_add_course(mesaj, titlu = titlu, continut = continut)


class delete_course(Handler):
	def get(self, curs_id):
		key = db.Key.from_path('Curs', int(curs_id), parent = blog_key())

		c = db.get(key)
		cursuri = db.GqlQuery("SELECT * FROM Curs WHERE categorie = '%s'" % c.categorie)
		if cursuri.count() == 1:
			categorie = db.GqlQuery("SELECT * FROM Category WHERE categorie = '%s'" % c.categorie)
			print categorie.count()
			for cat in categorie:
				cat.delete()
		c.delete()

		self.redirect("/")


class view_course(Handler):
	def get(self, curs_id):
		key = db.Key.from_path('Curs', int(curs_id), parent = blog_key())

		c = db.get(key)

		c.continut = textile.textile(c.continut)

		curs_from_cat = db.GqlQuery("SELECT * FROM Curs WHERE categorie = '%s'" % c.categorie)

		self.render("curs.html", curs = c, curs_from_cat = curs_from_cat)

class add_question(Handler):
	def get(self):
		self.render("add_question.html", mesaj = '')

	def post(self):
		_parent = self.request.get("_parent")

		correctAnswer = self.request.get("correctAnswer")
		answer1 = self.request.get("answer1")
		answer2 = self.request.get("answer2")
		answer3 = self.request.get("answer3")
		answer4 = self.request.get("answer4")
		question = self.request.get("question")

		correctAnswer = cgi.escape(correctAnswer)
		answer1 = cgi.escape(answer1)
		answer2 = cgi.escape(answer2)
		answer3 = cgi.escape(answer3)
		answer4 = cgi.escape(answer4)
		
		print _parent
		
		obj = Question(parent = blog_key(), question = question, _parent = _parent, answer1 = answer1, answer2 = answer2, answer3 = answer3, answer4 = answer4, correctAnswer = correctAnswer)
		obj.put()

		self.render("add_question.html", mesaj = "Intrebare adaugata cu succes!")

class quiz(Handler):
	q_total = 0
	def get_question(self, curs_id, question_number): #just simply go full retard
		questions = db.GqlQuery("SELECT * FROM Question WHERE _parent = '%s'" % curs_id)
		question_cur = 0;
		self.q_total = questions.count()
		question_number = int(question_number)
		for question in questions:
			question_cur = question_cur + 1
			if question_cur == question_number:
				return question

	def get(self, curs_id, question_number):
		question = self.get_question(curs_id, question_number)

		mesaj = ""
		question_number = int(question_number)
		lastOne = 0
		if question_number >= self.q_total:
			lastOne = 1
		else:
			lastOne = 0
		key = db.Key.from_path('Curs', int(curs_id), parent = blog_key())
		curs_name = db.get(key).titlu
		self.render("quiz.html", mesaj = mesaj, question = question, curs_id = curs_id, curs_name = curs_name, question_number = question_number + 1, lastOne = lastOne)

	def post(self, curs_id, question_number):
		answer = self.request.get("answer")
		question = self.get_question(curs_id, question_number)

		mesaj = ""

		if answer == question.correctAnswer:
			mesaj = "Raspuns corect!"
		else:
			mesaj = "Raspuns gresit, mai incearca!"


		question_number = int(question_number)
		lastOne = 0
		if question_number >= self.q_total:
			lastOne = 1
		else:
			lastOne = 0
		key = db.Key.from_path('Curs', int(curs_id), parent = blog_key())
		curs_name = db.get(key).titlu
		self.render("quiz.html", mesaj = mesaj, question = question, curs_id = curs_id, curs_name = curs_name, question_number = question_number + 1, lastOne = lastOne)


class CategoriiCursuri(Handler):
    def get(self):
    	categorii = db.GqlQuery("SELECT * FROM Category");
       	self.render("front.html", categorii = categorii)

class VeziCategorie(Handler):
	def get(self, categorie):
		cursuri = db.GqlQuery("SELECT * FROM Curs WHERE categorie = '%s'" % categorie)
		cat = db.GqlQuery("SELECT * FROM Category WHERE categorie = '%s'" % categorie).get()
		self.render("vezicursuri.html", cursuri = cursuri, categorie = cat)

class PozaCategorie(Handler):
	def get(self, categorie):
		self.render("modifica_poza_categorie.html", mesaj = "", categorie = categorie)
	def post(self, categorie):

		link = self.request.get("link_poza")

		categorii = db.GqlQuery("SELECT * FROM Category WHERE categorie = '%s'" % categorie)
		
		for cat in categorii:
			cat.link_poza = link
			cat.put()

		mesaj = "Link poza schimbat!"
		self.render("modifica_poza_categorie.html", mesaj = mesaj, categorie = categorie)


app = webapp2.WSGIApplication([
    ('/', CategoriiCursuri),
    (r'/adauga_curs/*(\d*)', add_course),
    (r'/curs/(\d+)', view_course),
    (r'/categorie/(.+)', VeziCategorie),
    (r'/pozacategorie/(.+)', PozaCategorie),
    (r'/sterge_curs/(\d+)', delete_course),
    (r'/quiz/(\d+)/(\d+)', quiz),
    ('/adauga_intrebare', add_question),
], debug=True)


