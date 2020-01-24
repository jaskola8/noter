from app import db, bcrypt, login_manager
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    _password = db.Column("password", db.String(120), nullable=False)
    _login_attempts = db.Column(db.Integer, default=0)
    _last_login_attempt = db.Column(db.DateTime)
    owned_notes = db.relationship('Note', backref="owner", lazy=True, cascade="all, delete-orphan")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password: str):
        self._password = bcrypt.generate_password_hash(password=password)

    def check_password(self, candidate: str) -> bool:
        if not bcrypt.check_password_hash(self._password, candidate):
            self._login_attempts += 1
            self._last_login_attempt = datetime.now()
            return False
        else:
            self._login_attempts = 0
            return True

    def change_password(self, old_pass: str, new_pass: str) -> bool:
        if self.check_password(old_pass):
            self.password = new_pass
            self.save()
            return True
        else:
            return False

    def can_login(self):
        minutes_since_last_login = (datetime.now() - self._last_login_attempt).min
        if minutes_since_last_login < 5 and self._login_attempts > 3:
            return False

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    user = None
    try:
        user_id = int(user_id)
        user = User.query.filter_by(id=user_id).first()
    except ValueError:
        pass
    return user


def initialize_users():
    admin = User(username="admin", password="admin")
    user = User(username="user", password="user")
    user.save()
    admin.save()
