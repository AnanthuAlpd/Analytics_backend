from models.menus import Menu
from models.roles import Role
from models.role_menus import RoleMenu
from db import db
from sqlalchemy.exc import SQLAlchemyError

class MenuService:

   @staticmethod
   def get_all_menus_with_roles():
        results = (
            db.session.query(Menu, Role)
            .outerjoin(RoleMenu, Menu.id == RoleMenu.menu_id)
            .outerjoin(Role, Role.id == RoleMenu.role_id)
            .all()
        )

        menu_dict = {}
        for menu, role in results:
            if menu.id not in menu_dict:
                menu_dict[menu.id] = {
                    "id": menu.id,
                    "title": menu.title,
                    "router_link": menu.router_link,
                    "href": menu.href,
                    "icon": menu.icon,
                    "target": menu.target,
                    "has_sub_menu": menu.has_sub_menu,
                    "parent_id": menu.parent_id,
                    "roles": []
                }
            if role:
                menu_dict[menu.id]["roles"].append({
                    "id": role.id,
                    "name": role.name
                })

        return list(menu_dict.values())
    
   @staticmethod
   def get_menus_by_roles(role_ids: list[int]):
        if not role_ids:
            return []

        results = (
            db.session.query(Menu)
            .join(RoleMenu, Menu.id == RoleMenu.menu_id)
            .join(Role, Role.id == RoleMenu.role_id)
            .filter(Role.id.in_(role_ids))   # support multiple roles
            .distinct()                      # avoid duplicate menus
            .all()
        )

        menus = []
        for menu in results:
            menus.append({
                "id": menu.id,
                "title": menu.title,
                "routerLink": menu.router_link,
                "href": menu.href,
                "icon": menu.icon,
                "target": menu.target,
                "hasSubMenu": menu.has_sub_menu,
                "parentId": menu.parent_id
            })
        return menus
   @staticmethod
   def create_menu(data: dict):
        try:
            new_menu = Menu(
                title=data.get("title"),
                router_link=data.get("router_link"),
                icon=data.get("icon"),
                has_sub_menu=data.get("has_sub_menu", False),
                parent_id=data.get("parent_id"),
                href=data.get("href"),
                target=data.get("target")
            )
            db.session.add(new_menu)
            db.session.commit()

            # Assign roles
            roles = data.get("roles", [])
            for role in roles:
                role_id = role["id"] if isinstance(role, dict) else role
                db.session.add(RoleMenu(menu_id=new_menu.id, role_id=role_id))

            db.session.commit()
            return {"data": MenuService.get_menu_with_roles(new_menu.id), "message": "Menu created successfully", "code": 201}

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": f"Error creating menu: {str(e)}", "status": "error", "code": 500}

   @staticmethod
   def update_menu(menu_id: int, data: dict):
        try:
            menu = Menu.query.get(menu_id)
            if not menu:
                return {"message": "Menu not found", "status": "error", "code": 404}

            menu.title = data.get("title", menu.title)
            menu.router_link = data.get("router_link", menu.router_link)
            menu.icon = data.get("icon", menu.icon)
            menu.has_sub_menu = data.get("has_sub_menu", menu.has_sub_menu)
            menu.parent_id = data.get("parent_id", menu.parent_id)
            menu.href = data.get("href", menu.href)
            menu.target = data.get("target", menu.target)

            # Remove old role mappings
            RoleMenu.query.filter_by(menu_id=menu.id).delete()

            # Add new role mappings
            roles = data.get("roles", [])
            for role in roles:
                role_id = role["id"] if isinstance(role, dict) else role
                db.session.add(RoleMenu(menu_id=menu.id, role_id=role_id))

            db.session.commit()
            return {"data": MenuService.get_menu_with_roles(menu.id), "message": "Menu updated successfully", "code": 200}

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": f"Error updating menu: {str(e)}", "status": "error", "code": 500}

   @staticmethod
   def delete_menu(menu_id: int):
        try:
            menu = Menu.query.get(menu_id)
            if not menu:
                return {"message": "Menu not found", "status": "error", "code": 404}

            RoleMenu.query.filter_by(menu_id=menu_id).delete()
            db.session.delete(menu)
            db.session.commit()
            return {"message": "Menu deleted successfully", "code": 200}

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": f"Error deleting menu: {str(e)}", "status": "error", "code": 500}

   @staticmethod
   def get_menu_with_roles(menu_id: int):
        menu = Menu.query.get(menu_id)
        if not menu:
            return None

        roles = (
            db.session.query(Role)
            .join(RoleMenu, Role.id == RoleMenu.role_id)
            .filter(RoleMenu.menu_id == menu.id)
            .all()
        )

        return {
            "id": menu.id,
            "title": menu.title,
            "router_link": menu.router_link,
            "href": menu.href,
            "icon": menu.icon,
            "target": menu.target,
            "has_sub_menu": menu.has_sub_menu,
            "parent_id": menu.parent_id,
            "roles": [{"id": r.id, "name": r.name} for r in roles]
        }