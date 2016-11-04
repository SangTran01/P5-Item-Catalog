from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Collection, ArtWork

engine = create_engine('sqlite:///artcollections.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture=('https://pbs.twimg.com/profile_images/'
                      '2671170543/18debd694829ed78203a5a36dd'
                      '364160_400x400.png'))
session.add(User1)
session.commit()

# dummy collection1
collection1 = Collection(user_id=1, name="Renaissance Works")

session.add(collection1)
session.commit()

# dummy artwork
artwork1 = ArtWork(user_id=1,
                   picture=("https://upload.wikimedia.org/wikipedia/"
                            "commons/d/d5/Mona_Lisa_(copy,_Hermitage).jpg"),
                   name="Mona Lisa", description="Lady Smile in painting",
                   price="$200.00", collection=collection1)

session.add(artwork1)
session.commit()

artwork2 = ArtWork(user_id=1,
                   picture=("https://s-media-cache-ak0.pinimg.com/236x/"
                            "01/d2/c7/01d2c7787c854911ce58b7b86d550caf.jpg"),
                   name="Water Lily", description="Water Lily painting",
                   price="$300.00", collection=collection1)

session.add(artwork2)
session.commit()

artwork3 = ArtWork(user_id=1,
                   picture=("http://www.ducksters.com/history/"
                            "renaissance_school_of_athens.jpg"),
                   name="Example 3", description="Example of example 3",
                   price="$200.00", collection=collection1)

session.add(artwork3)
session.commit()

artwork4 = ArtWork(user_id=1,
                   picture=("http://cdn.rsvlts.com/wp-content/uploads/2014/"
                            "11/165833_460764387267417_212236084_n.jpg"),
                   name="Example 4", description="Example of example 4",
                   price="$300.00", collection=collection1)

session.add(artwork4)
session.commit()

# Collection2
collection2 = Collection(user_id=1, name="Timeless")

session.add(collection1)
session.commit()

# dummy artwork
artwork1 = ArtWork(user_id=1, picture="https://afremov.com/image.php?"
                   "type=P&id=18000",
                   name="Raining", description="Walking in the rain",
                   price="$200.00", collection=collection2)

session.add(artwork1)
session.commit()

artwork2 = ArtWork(user_id=1,
                   picture=("http://img09.deviantart.net/b6c5/i/2015/"
                            "268/f/6/deep_hug_by_leonid_afremov_by_"
                            "leonidafremov-d6gxdfs.jpg"),
                   name="Deep Hug", description="People hug",
                   price="$300.00", collection=collection2)

session.add(artwork2)
session.commit()

# dummy artwork
artwork3 = ArtWork(user_id=1,
                   picture=("https://s-media-cache-ak0.pinimg.com/236x/"
                            "c9/01/58/c90158a8683038caf1f147adea706305.jpg"),
                   name="Some picture", description="Testing 123",
                   price="$200.00", collection=collection2)

session.add(artwork3)
session.commit()

artwork4 = ArtWork(user_id=1,
                   picture=("http://i.ebayimg.com/images/g/HQMAAOxyzi9Sfpd5/"
                            "s-l300.jpg"),
                   name="Walking", description="People walking",
                   price="$300.00", collection=collection2)

session.add(artwork4)
session.commit()


collection3 = Collection(user_id=1, name="This Normal?")

session.add(collection1)
session.commit()

# dummy artwork
artwork1 = ArtWork(user_id=1,
                   picture=("http://cdn.infomory.com/wp-content/uploads/"
                            "2013/12/Picasso_The_Weeping_Woman_Tate_"
                            "identifier_T05010_10-492x450.jpg"),
                   name="Sneezing", description="Covering mouth before sneeze",
                   price="$200.00", collection=collection3)

session.add(artwork1)
session.commit()

artwork2 = ArtWork(user_id=1,
                   picture=("http://www.ebsqart.com/Art/Gallery/"
                            "Acrylics-Colored-Pencils-Pastels-Glitter/"
                            "639098/650/650/WHITE-PERSIAN-CAT-ODD-EYE-"
                            "AT-THE-BEACH.jpg"),
                   name="Cat", description="Cat staring at me",
                   price="$100.00", collection=collection3)

session.add(artwork2)
session.commit()

# dummy artwork
artwork3 = ArtWork(user_id=1,
                   picture=("https://ae01.alicdn.com/kf/"
                            "HTB1ww6DLXXXXXaPXXXXq6xXFXXXd/Colorful-"
                            "Handpainted-Wall-Pictures-Lady-Figure-"
                            "Portrait-font-b-Oil-b-"
                            "font-font-b-Paintings-b.jpg"),
                   name="What was this", description="I forgot the name",
                   price="$200.00", collection=collection3)

session.add(artwork3)
session.commit()

artwork4 = ArtWork(user_id=1,
                   picture=("http://www.abstractartistgallery.org/"
                            "wp-content/uploads/2012/12/Theresa-Paden-Abstract"
                            "-Artist-Abstract-Art-Painting-2.jpg"),
                   name="Example image", description="How are you?",
                   price="$100.00", collection=collection3)

session.add(artwork4)
session.commit()


print "added menu items!"
