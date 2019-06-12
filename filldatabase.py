#!/usr/bin/env python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


category1 = Category(name="Soccer")
session.add(category1)
session.commit()

category2 = Category(name="Basketball")
session.add(category2)
session.commit()

category3 = Category(name="Baseball")
session.add(category3)
session.commit()

category4 = Category(name="Frisbee")
session.add(category4)
session.commit()

category5 = Category(name="Snowboarding")
session.add(category5)
session.commit()

category6 = Category(name="Rock Climbing")
session.add(category6)
session.commit()

category7 = Category(name="Foosball")
session.add(category7)
session.commit()

category8 = Category(name="Skating")
session.add(category8)
session.commit()

category9 = Category(name="Hockey")
session.add(category9)
session.commit()

catalogItem1 = Item(
    name="Frisbee Disc",
    description="A plastic flying disc. Perfect for a game of ultimate frisbee.",
    category=category4, user_id=1)
session.add(catalogItem1)
session.commit()

catalogItem2 = Item(
    name="Soccer Ball",
    description="An inflatable soccer ball. Size 4.",
    category=category1, user_id=1)
session.add(catalogItem2)
session.commit()

catalogItem3 = Item(
    name="Junior's Soccer Cleats",
    description="Green and black soccer cleats for 4-8 year olds.",
    category=category1, user_id=1)
session.add(catalogItem3)
session.commit()

catalogItem4 = Item(
    name="Adult Soccer Cleats",
    description="Soccer cleats with a synthetic upper and rubber molded cleats.",
    category=category1, user_id=1)
session.add(catalogItem4)
session.commit()

catalogItem5 = Item(
    name="Basketball Shorts",
    description="Mesh panels with a knee length hem. Machine wash cold.",
    category=category2, user_id=1)
session.add(catalogItem5)
session.commit()

catalogItem6 = Item(
    name="Wooden Baseball Bat",
    description="Wooden bat made of series 3X Ash with a Natural finish. Dimensions: 35 x 3 x 3 inches ",
    category=category3, user_id=1)
session.add(catalogItem6)
session.commit()

catalogItem7 = Item(
                name="Hockey Stick",
                description="60\" reinforced laminated shaft with a wrapped carbon blade. Ideal street and ice hockey",
                category=category9, user_id=1)
session.add(catalogItem7)
session.commit()

catalogItem8 = Item(
                name="Inline Skates",
                description="High quality skates with a triple buckly closure and indoor/outdoor wheels.",
                category=category8, user_id=1)
session.add(catalogItem8)
session.commit()

catalogItem9 = Item(
                name="Foosball Table",
                description="A popular and classic arcade game. Standard size (56\") with very little assembly.",
                category=category7, user_id=1)
session.add(catalogItem9)
session.commit()

catalogItem10 = Item(
                name="Snowboard",
                description="A snowboard with a trendy design. Has adjustable stepin bindings. Very user friendly.",
                category=category5, user_id=1)
session.add(catalogItem10)
session.commit()

catalogItem11 = Item(
    name="Climbing Harness",
    description="Made of polyester. Fits waists from 20\" to 53\". Harness weight limited to 300KG. Perfect for rock climbing and indoor climbing. Backed by a 12 month warranty. ",
    category=category6, user_id=1)
session.add(catalogItem11)
session.commit()


print "added items and categories to the catalog"
