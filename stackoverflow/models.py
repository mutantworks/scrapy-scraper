from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    Base.metadata.create_all(engine)


# Association Table for Many-to-Many relationship between Question and Tag
question_tag = Table('question_tag', Base.metadata,
    Column('question_id', Integer, ForeignKey('question.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    stack_user_id = Column('stack_user_id', Text())
    name = Column('name', String(50))
    reputation_score = Column('reputation_score', Text())
    gold_badges = Column('gold_badages', Text())
    silver_badges = Column('silver_badages', Text())
    bronze_badges = Column('bronze_badages', Text())
    questions = relationship('Question', backref='user')  # One user to many Questions
    answers = relationship('Answer', backref='user')  # One user to many Answers


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(30), unique=True)
    # questions = relationship('Question', secondary='question_tag',
    #     lazy='dynamic', backref="tag")  # M-to-M for question and tag


class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True)
    stack_question_id = Column('stack_question_id', Text())
    question_title = Column('question_title', Text())
    question_content = Column('question_content', Text())
    question_url = Column('question_url', Text())
    user_id = Column(Integer, ForeignKey('user.id'))  # Many question to one user
    date_posted = Column('date_posted', Text())
    upvote = Column('upvote', Text())
    view = Column('view', Text())
    answers_count = Column('answer_count', Text())
    tags = relationship('Tag', secondary='question_tag',
        lazy='dynamic', backref="question")  # M-to-M for question and tag
    answers = relationship('Answer', backref='question')  # One Question to many Answers
    comments = relationship('QuestionComment', backref='question') # ONe question to many Comments


class Answer(Base):
    __tablename__ = "answer"

    id = Column(Integer, primary_key=True)
    stack_answer_id = Column('stack_answer_id', Text())
    answer_content = Column('answer_content', Text())
    user_id = Column(Integer, ForeignKey('user.id'))  # Many answers to one user
    question_id = Column(Integer, ForeignKey('question.id'))  # Many answers to one question
    date_posted = Column('date_posted', Text())
    upvote = Column('upvote', Text())
    accepted = Column('accepted', Text())
    comments = relationship('AnswerComment', backref='answer')  # ONe question to many Comments


class QuestionComment(Base):
    __tablename__ = "questioncomment"

    id = Column(Integer, primary_key=True)
    stack_question_comment_id = Column('stack_question_comment_id', Text())
    comment_content = Column('comment_content', Text())
    username = Column('username', Text())
    question_id = Column(Integer, ForeignKey('question.id'))  # Many comments to one user
    stack_question_id = Column('stack_question_id', Text())


class AnswerComment(Base):
    __tablename__ = "answercomment"

    id = Column(Integer, primary_key=True)
    stack_answer_comment_id = Column('stack_answer_comment_id', Text())
    comment_content = Column('comment_content', Text())
    username = Column('username', Text())
    answer_id = Column(Integer, ForeignKey('answer.id'))  # Many comments to one user
    stack_answer_id = Column('stack_answer_id', Text())