#!/usr/bin/env python
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(80))
    id = Column(Integer, primary_key=True)


class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    items = relationship("Item")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'category_id': self.id,
            'category_name': self.name,
            'category_items': [item.serialize for item in self.items]
        }


class Item(Base):
    __tablename__ = 'item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, back_populates='items')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'item_id': self.id,
            'item_name': self.name,
            'item_description': self.description,
            'category_id': self.category_id
        }


engine = create_engine('sqlite:///catalogwithusers.db')


Base.metadata.create_all(engine)
