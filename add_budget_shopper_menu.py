from app import create_app
from db import db
from models.menus import Menu
from models.roles import Role
from models.role_menus import RoleMenu

def setup_guest_role_and_menus():
    app = create_app()
    with app.app_context():
        print("Starting Guest Role and Menu setup...")

        # 1. Create or ensure 'Guest User' Role exists
        guest_role = Role.query.filter_by(name='Guest User').first()
        if not guest_role:
            guest_role = Role(name='Guest User', description='Demo-only access role')
            db.session.add(guest_role)
            db.session.flush() # get the ID
            print(f"-> Created new role 'Guest User' with ID: {guest_role.id}")
        else:
            print(f"-> Role 'Guest User' already exists with ID: {guest_role.id}")

        # 2. Add or ensure 'Demo Dashboard' menu exists
        demo_menu = Menu.query.filter_by(title='Demo Dashboard').first()
        if not demo_menu:
            demo_menu = Menu(
                title='Demo Dashboard',
                router_link='/dashboard/demo',
                icon='dashboard',
                has_sub_menu=False
            )
            db.session.add(demo_menu)
            db.session.flush()
            print(f"-> Created 'Demo Dashboard' menu with ID: {demo_menu.id}")
        else:
            print(f"-> Menu 'Demo Dashboard' exists with ID: {demo_menu.id}")

        # 3. Add or ensure 'Budget Shopper' menu exists
        budget_menu = Menu.query.filter_by(title='Budget Shopper').first()
        if not budget_menu:
            budget_menu = Menu(
                title='Budget Shopper',
                router_link='/dashboard/budget-shopper',
                icon='account_balance_wallet',
                has_sub_menu=False
            )
            db.session.add(budget_menu)
            db.session.flush()
            print(f"-> Created 'Budget Shopper' menu with ID: {budget_menu.id}")
        else:
            print(f"-> Menu 'Budget Shopper' exists with ID: {budget_menu.id}")


        # 4. Map Menus to the Guest Role if not already mapped
        # Check Demo Dashboard Mapping
        existing_demo_map = RoleMenu.query.filter_by(role_id=guest_role.id, menu_id=demo_menu.id).first()
        if not existing_demo_map:
            db.session.add(RoleMenu(role_id=guest_role.id, menu_id=demo_menu.id))
            print("-> Mapped 'Demo Dashboard' to 'Guest User'")

        # Check Budget Shopper Mapping
        existing_budget_map = RoleMenu.query.filter_by(role_id=guest_role.id, menu_id=budget_menu.id).first()
        if not existing_budget_map:
            db.session.add(RoleMenu(role_id=guest_role.id, menu_id=budget_menu.id))
            print("-> Mapped 'Budget Shopper' to 'Guest User'")

        db.session.commit()
        print("Setup complete! Database changes saved successfully.")

if __name__ == '__main__':
    setup_guest_role_and_menus()
