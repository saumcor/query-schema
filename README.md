# query-schema

Use marhsmallow-sqlalchemy schemas to optimally construct ORM queries

ORM Models, contain attributes and relationships with other Models, which may
or may not be required when serializing the models.

By using the schema's required attributes, this library tries to optimize the ORM query.

This helps solve the N+1 query probelms most ORMs have.

## Installation

```sh
$ pip install -e .
```

## Usage

```py
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from query_schema import QuerySchema

engine = sa.create_engine("sqlite:///:memory:")
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

## models.py

class Author(Base):
    __tablename__ = "authors"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)

    def __repr__(self):
        return f"<Author(name={self.name})>"


class Book(Base):
    __tablename__ = "books"
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    author_id = sa.Column(sa.Integer, sa.ForeignKey("authors.id"))
    author = relationship("Author", backref=backref("books"))

    def __repr__(self):
        return f"<Book(name={self.title})>"

Base.metadata.create_all(engine)

## schema.py

class AuthorSchema(SQLAlchemySchema, QuerySchema):
    class Meta:
        model = Author

    id = auto_field()
    name = auto_field()
    books = auto_field()

class BookSchema(SQLAlchemySchema, QuerySchema):
    class Meta:
        model = Book

    id = auto_field()
    title = auto_field()
    author = fields.Nested(AuthorSchema)

## Usage:
# Queries on Book should use selectinload(Author) by default
session.query(Book).options(BookSchema.query_options()).all()
```
