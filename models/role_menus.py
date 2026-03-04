from db import db
from models.roles import Role
from models.menus import Menu

class RoleMenu(db.Model):
    __tablename__ = 'role_menus'

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True, nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), primary_key=True, nullable=False)

    role = db.relationship('Role', backref=db.backref('role_menus', lazy=True))
    menu = db.relationship('Menu', backref=db.backref('role_menus', lazy=True))

    def __repr__(self):
        return f"<RoleMenu role_id={self.role_id} menu_id={self.menu_id}>"
