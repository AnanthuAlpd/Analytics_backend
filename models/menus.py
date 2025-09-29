from db import db

class Menu(db.Model):
    __tablename__ = 'menus'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    router_link = db.Column(db.String(255), nullable=True)
    href = db.Column(db.String(255), nullable=True)
    icon = db.Column(db.String(100), nullable=True)
    target = db.Column(db.String(50), nullable=True)
    has_sub_menu = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=True)

    # Self-referencing relationship for submenus
    parent = db.relationship(
        'Menu',
        remote_side=[id],
        backref=db.backref('sub_menus', cascade='all, delete-orphan', lazy=True)
    )

    def __repr__(self):
        return f"<Menu {self.title}>"
