from datetime import datetime, timezone
from werkzeug.security import check_password_hash

from .extensions import db


class User(db.Model):
    __tablename__ = "users"

    tasks = db.relationship("Task", back_populates="user")

    role = db.Column(
        db.String(20),
        nullable=False,
        default="user",
        server_default="user"
    )

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def check_password(self, candidate_password):
        return check_password_hash(
            self.password_hash,
            candidate_password
        )

    def __repr__(self):
        return f"<User {self.email}>"
    
class Task(db.Model):
    __tablename__ = "tasks"

    user = db.relationship("User", back_populates="tasks")

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    completed = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )