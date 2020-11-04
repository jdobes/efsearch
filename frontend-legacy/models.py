from peewee import *
from efsearch import db

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = db

class Pagecategory(BaseModel):
    name = TextField(null=True)

    class Meta:
        db_table = 'page_category'

class Page(BaseModel):
    page_category = ForeignKeyField(Pagecategory)
    created = DateTimeField(null=True)
    name = TextField(null=True)
    ef_id = IntegerField()

    class Meta:
        db_table = 'page'

class Account(BaseModel):
    name = TextField(unique=True)

    class Meta:
        db_table = 'account'

class Post(BaseModel):
    account = ForeignKeyField(Account)
    body = TextField(index=True, null=True)
    created = DateTimeField(index=True, null=True)
    anchor = IntegerField(db_column='ef_id', index=True, null=True)
    funny_ranking = IntegerField(index=True, null=True)
    page = ForeignKeyField(Page)
    parent_anchor = IntegerField(db_column='parent_ef_id', index=True, null=True)

    class Meta:
        db_table = 'post'

class Postcache(BaseModel):
    name = TextField(primary_key=True, unique=True)
    count = IntegerField()

    class Meta:
        db_table = 'post_cache'
