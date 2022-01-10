from proj.app.settings import engine, Session
from proj.app.dbops import Base, Location, Department, Category, SubCategory


def populate():
    Base.metadata.create_all(engine)
    with Session() as session:
        loc1 = Location(name="Perimeter")
        loc2 = Location(name='Center')
        dept1 = Department(name="Bakery")
        dept2 = Department(name="Dairy")
        dept3 = Department(name="Frozen")
        loc1.departments = [dept1]
        loc2.departments = [dept2, dept3]
        cat1 = Category(name="Bakery Bread")
        cat2 = Category(name="In Store Bakery")
        cat3 = Category(name="Cheese")
        cat4 = Category(name="Cream or Creamer")
        cat5 = Category(name="Frozen Bake")
        dept1.categories = [cat1, cat2]
        dept2.categories = [cat3, cat4]
        dept3.categories = [cat5]
        scat1 = SubCategory(name='Bagels')
        scat1.category = cat1
        scat2 = SubCategory(name='Baking or Breading Products')
        scat2.category = cat1
        scat3 = SubCategory(name='English Muffins or Biscuits')
        scat3.category = cat1
        scat4 = SubCategory(name='Flatbreads')
        scat4.category = cat1
        scat5 = SubCategory(name='Breakfast Cake or Sweet Roll')
        scat5.category = cat2
        scat6 = SubCategory(name='Cakes')
        scat6.category = cat2
        scat7 = SubCategory(name='Pies')
        scat7.category = cat2
        scat8 = SubCategory(name='Seasonal')
        scat8.category = cat2
        scat9 = SubCategory(name='Cheese Sauce')
        scat9.category = cat3
        scat10 = SubCategory(name='Specialty Cheese')
        scat10.category = cat3
        scat11 = SubCategory(name='Dairy Alternative Creamer')
        scat11.category = cat4
        scat12 = SubCategory(name='Bread or Dough Products Frozen')
        scat12.category = cat5
        scat13 = SubCategory(name='Breakfast Cake or Sweet Roll Frozen')
        scat13.category = cat5
        session.add_all([
            loc1,
            loc2
        ])
        session.commit()