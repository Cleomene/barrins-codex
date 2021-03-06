import copy
import urllib.parse
import re
import unidecode

import flask
import flask_babel
import jinja2.exceptions

from . import config
from . import navigation


app = flask.Flask(__name__, template_folder="templates")
app.jinja_env.policies["ext.i18n.trimmed"] = True
babel = flask_babel.Babel(app)
config.configure_app(app)


def main():
	app.run()


# Retrieving locale and timezone information
@babel.localeselector
def get_locale():
	return flask.g.get("lang_code", app.config["BABEL_DEFAULT_LOCALE"])


@babel.timezoneselector
def get_timezone():
	user = flask.g.get("user", None)
	if user is not None:
		return user.timezone


# Defining Errors
@app.errorhandler(jinja2.exceptions.TemplateNotFound)
@app.errorhandler(404)
def page_not_found(error):
	return flask.render_template("404.html"), 404


# favicon redirection - need when serving card images directly
@app.route("/favicon.ico")
def favicon():
	return flask.redirect(flask.url_for("static", filename="img/favicon.ico"))


# Default route
@app.route("/")
@app.route("/<path:page>")
@app.route("/<lang_code>/<path:page>")
def index(lang_code=None, page=None):
	redirect = False
	if not page:
		page = "index.html"
		redirect = True
	if not lang_code or lang_code not in app.config["SUPPORTED_LANGUAGES"].keys():
		if lang_code:
			page = lang_code + "/" + page
		lang_code = flask.request.accept_languages.best_match(
			app.config["SUPPORTED_LANGUAGES"].keys()
		)
		page = "/" + lang_code + "/" + page
		redirect = True
	if redirect:
		return flask.redirect(page, 301)

	flask.g.lang_code = lang_code
	return flask.render_template(page)


def _i18n_url(page, _anchor=None, locale=None, **params):
	url = "/" + (locale or get_locale()) + page.url
	if params:
		url += "?" + urllib.parse.urlencode(params)
	if _anchor:
		url += "#" + _anchor
	return url


def _link(page, name=None, _anchor=None, _class=None, locale=None, **params):
	if not page or not page.url:
		return ""
	name = name or page.name
	url = _i18n_url(page, _anchor, locale, **params)
	if _class:
		_class = f"class={_class} "
	else:
		_class = ""
	return flask.Markup(f'<a {_class}href="{url}">{name}</a>')


@app.context_processor
def linker():
	path = flask.request.path
	if path[1:3] in app.config["SUPPORTED_LANGUAGES"].keys():
		path = path[3:]
	if path[-11:] == "/index.html":
		path = path[:-11]
	if path[-5:] == ".html":
		path = path[:-5]
	if path[-1:] == "/":
		path = path[:-1]

	def i18n_url(page, _anchor=None, **params):
		return _i18n_url(
			navigation.HELPER.get(page, {}).get("self"), _anchor=_anchor, **params
		)

	def link(page, name=None, _anchor=None, **params):
		return _link(
			navigation.HELPER.get(page, {}).get("self"),
			name=name,
			_anchor=_anchor,
			**params,
		)

	def translation(locale, name):
		return _link(
			navigation.HELPER.get(path, {}).get("self"), name=name, locale=locale
		)

	def top():
		return _link(navigation.HELPER.get(path, {}).get("top"))

	def next():
		return _link(navigation.HELPER.get(path, {}).get("next"), _class="next")

	def prev():
		return _link(navigation.HELPER.get(path, {}).get("prev"), _class="prev")

	def external(url, name):
		return flask.Markup(f'<a target="_blank" href="{url}">{name}</a>')

	return dict(
		i18n_url=i18n_url,
		link=link,
		translation=translation,
		top=top,
		next=next,
		prev=prev,
		external=external,
	)


def file_name(name):
	name = unidecode.unidecode(name).lower()
	name = re.sub(r"[^a-zA-Z0-9]", " ", name)
	return name


@app.context_processor
def display_card():
	def card(name, display_name=None):
		return flask.Markup(
			"""<span class="card" onclick="dC('{fname}')" onmouseover="hC('{fname}')" onmouseout="oC()">{name}</span>""".format(
				# replace spaces with non-breakable spaces in card names
				name=(display_name or name).replace(" ", " "),
				fname=file_name(name),
			)
		)

	def card_image(name, hover=True):
		img = '<img src="{fname}" alt="{name}" onclick="dC(\'{fname}\')"'
		if hover:
			img += ' onmouseover="hC(\'{fname}\')" onmouseout="oC()"'
		img += "/>"
		return flask.Markup(img.format(name=name, fname=file_name(name),))

	return dict(card=card, card_image=card_image)
