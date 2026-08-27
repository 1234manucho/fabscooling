from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Inquiry(db.Model):
    __tablename__ = "inquiries"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(24), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(160))
    email = db.Column(db.String(160), nullable=False, index=True)
    phone = db.Column(db.String(50))
    solution = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(160))
    target_temperature = db.Column(db.String(60))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="new", index=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Inquiry {self.reference}>"


class NewsletterSubscriber(db.Model):
    __tablename__ = "newsletter_subscribers"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
