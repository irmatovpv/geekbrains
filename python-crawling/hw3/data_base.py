import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
import models
from settings import load_config

load_config()
db_uri = os.getenv("DATABASE")

metadata = MetaData()
engine = create_engine(db_uri)
models.Base.metadata.create_all(bind=engine)
session_maker = sessionmaker(bind=engine)

class Storage:
    def __init__(self):
        self.db = session_maker()
        pass

    def create_or_get_tag(self, tag):
        db = self.db
        tmp_tag = db.query(models.Tag).filter(models.Tag.url == tag['url']).first()
        if not tmp_tag:
            tmp_tag = models.Tag(**tag)
            try:
                db.add(tmp_tag)
                db.commit()
            except Exception:
                db.rollback()
        return tmp_tag

    def store(self, data):
        db = self.db

        tags = [self.create_or_get_tag(tag) for tag in data['tags']]
        author=self.create_or_get_author(data['author'])

        tmp_post = db.query(models.Post).filter(models.Post.url == data['url']).first()
        if not tmp_post:
            tmp_post = models.Post(
                url=data['url'],
                title=data['title'],
                first_img=data['first_img'],
                date_published=data['date_published']
            )
        tmp_post.tags.extend(tags)
        tmp_post.writer=author
        self.store_comments(data['comments'], tmp_post)
        try:
            db.add(tmp_post)
            db.commit()
        except Exception:
            db.rollback()

    def create_or_get_author(self, author):
        db = self.db
        tmp_author = db.query(models.Writer).filter(models.Writer.url == author['url']).first()
        if not tmp_author:
            tmp_author = models.Writer(**author)
            try:
                db.add(tmp_author)
                db.commit()
            except Exception:
                db.rollback()
        return tmp_author

    def store_comment(self, comment, post):
        db = self.db
        tmp_comment = db.query(models.Comment).filter(models.Comment.external_id == comment['id']).first()
        parent_comment = None
        if comment.get('parent_id'):
            parent_comment = db.query(models.Comment).filter(models.Comment.external_id == comment['parent_id']).first()

        if not tmp_comment:
            tmp_comment = models.Comment(
                external_id = comment['id'],
                body = comment['body'],
                author = comment['author']['name'],
            )
            if parent_comment:
                tmp_comment.parent_id = parent_comment.id
            tmp_comment.post = post
            try:
                db.add(tmp_comment)
                db.commit()
            except Exception:
                db.rollback()
        return tmp_comment

    def store_comments(self, comments, post):
        result = []
        for comment in comments:
            result.append(self.store_comment(comment, post))
        return result
