from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey


Base = declarative_base()


class Location(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
    name = Column('name', String(50))
    
    def __repr__(self):
        return "<Location='%s'>" % self.name
    
    
class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'))
    name = Column('name', String(50))
    location = relationship("Location", back_populates="departments")
    
    def __repr__(self):
        return "<Department='%s')>" % self.name


Location.departments = relationship("Department", order_by=Department.id, back_populates="location")


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey('departments.id'))
    name = Column('name', String(50))
    department = relationship("Department", back_populates="categories")
    
    def __repr__(self):
        return "<Category='%s')>" % self.name


Department.categories = relationship("Category", order_by=Category.id, back_populates="department")


class SubCategory(Base):
    __tablename__ = 'sub_categories'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    name = Column('name', String(50))
    category = relationship("Category", back_populates="sub_catagories")
    
    def __repr__(self):
        return "<SubCategory='%s')>" % self.name


Category.sub_catagories = relationship("SubCategory", order_by=SubCategory.id, back_populates="category")
