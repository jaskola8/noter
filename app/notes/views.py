from flask import Blueprint, request, url_for, current_app, render_template, flash, abort, redirect
from flask_login import fresh_login_required, current_user
from .models import Note, asso
from app.auth.models import User
from .forms import NewNoteForm, EditNoteForm
from flask_wtf import FlaskForm

notes = Blueprint('notes', __name__)
@notes.before_request
@fresh_login_required
def before_request():
    pass


def check_access_level(note: Note):
    access = None
    if note.is_public or current_user in note.can_access:
        access = "read"
    if note.owner_id == current_user.id:
        access = "write"
    return access


@notes.route("/new", methods=["GET", "POST"])
def new_note():
    note = Note()
    form = NewNoteForm()
    users = User.query.filter(User.id != current_user.id).order_by(User.username).all()
    form.give_access.choices = [(u.id, u.username) for u in users]
    if form.validate_on_submit():
        note.content = form.content.data
        note.title = form.title.data
        note.is_public = form.is_public.data
        note.owner_id = current_user.id
        note.can_access = list(filter(lambda u: u.id in form.give_access.data, users))
        note.save()
        flash('Note created')
        return redirect(url_for('notes.show_note', note_id=note.id))
    elif request.method == "POST":
        flash("Invalid data provided")
    return render_template('notes/new_note_form.html', form=form)


@notes.route("/<note_id>/edit", methods=["GET", "POST"])
def edit_note(note_id: str):
    note = Note.query.filter_by(id=note_id).first_or_404()
    if check_access_level(note) != "write":
        abort(401)
    form = EditNoteForm()
    form.title.data = note.title
    form.content.data = note.content
    revoke_access_choices = note.can_access
    available_users = User.query.filter(User.id != note.owner_id).order_by(User.username).all()
    give_access_choices = list(filter(lambda u: u not in revoke_access_choices, available_users))
    form.give_access.choices = [(u.id, u.username) for u in give_access_choices]
    form.revoke_access.choices = [(u.id, u.username) for u in note.can_access]
    form.is_public.data = note.is_public
    if form.validate_on_submit():
        note.content = form.content.data
        note.title = form.title.data
        note.is_public = form.is_public.data
        to_give_access = list(filter(lambda u: u.id in form.give_access.data, give_access_choices))
        to_revoke_access = list(filter(lambda u: u.id in form.revoke_access.data, note.can_access))
        note.make_visible_for_users(to_give_access)
        note.hide_from_users(to_revoke_access)
        note.save()
        flash('Note updated')
        return redirect(url_for('notes.show_note', note_id=note.id))
    elif request.method == "POST":
        flash("Invalid data provided")
    return render_template('notes/edit_note_form.html', form=form)


@notes.route("/<note_id>/delete", methods=["GET", "POST"])
def delete_note(note_id: str):
    note = Note.query.filter_by(id=note_id).first_or_404()
    form = FlaskForm()
    if check_access_level(note) != "write":
        abort(401)
    if request.method == "POST":
        note.remove()
        flash("Note deleted")
        return redirect(url_for("notes.index"))
    else:
        return render_template('notes/confirm_delete.html', form=form, note=note)


@notes.route("/<note_id>/show", methods=["GET"])
def show_note(note_id: str):
    note = Note.query.filter_by(id=note_id).first_or_404()
    access = check_access_level(note)
    if access is None:
        abort(401)
    return render_template("notes/details.html", access=access, note=note,
                           owner=User.query.filter_by(id=note.owner_id).first_or_404())


@notes.route("/owned")
def owned_notes():
    return list_notes(current_user.owned_notes, access="write")


@notes.route("/shared")
def shared_notes():
    return list_notes(current_user.accessible_notes, access="read")


@notes.route("/public")
def public_notes():
    return list_notes(Note.query.filter_by(is_public=True).all(), access="read")


def list_notes(note_list, access):
    return render_template('notes/list.html', notes=note_list, access=access)


@notes.route("/", methods=["GET"])
def index():
    return render_template('notes/index.html')
