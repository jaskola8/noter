from app import db
from app.auth.models import User

asso = db.Table('asso',
                 db.Column('note_id', db.Integer, db.ForeignKey('note.id')),
                 db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                 )


class Note(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(120), default="Title")
    content = db.Column(db.Text(), default="Text")
    is_public = db.Column(db.Boolean(), default=False)
    owner_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    can_access = db.relationship('User', secondary=asso, lazy=True, backref=db.backref('accessible_notes', lazy='subquery'))

    def get_id(self):
        return str(self.id)

    def make_visible_for_users(self, users):
        for user in users:
            if user not in self.can_access:
                self.can_access.append(user)
        db.session.commit()

    def hide_from_users(self, users):
        for user in users:
            if user in self.can_access and user.id != self.owner_id:
                self.can_access.remove(user)
        db.session.commit()

    def hide_from_all(self):
        self.can_access.clear()
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()


def initialize_notes():
    note = Note(title="Title", content="Content", owner_id=0)
    note.save()
