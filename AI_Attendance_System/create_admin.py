from getpass import getpass

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import Admin


app = create_app()


with app.app_context():

    username = input("Enter admin username: ").strip()

    if not username:
        print("Username cannot be empty.")
        raise SystemExit

    existing_admin = Admin.query.filter_by(
        username=username
    ).first()

    if existing_admin:
        print("An admin with this username already exists.")
        raise SystemExit

    password = getpass(
        "Enter admin password: "
    )

    confirm_password = getpass(
        "Confirm admin password: "
    )

    if not password:
        print("Password cannot be empty.")
        raise SystemExit

    if password != confirm_password:
        print("Passwords do not match.")
        raise SystemExit

    hashed_password = generate_password_hash(
        password
    )

    admin = Admin(
        username=username,
        password=hashed_password
    )

    db.session.add(admin)
    db.session.commit()

    print(
        f"Admin '{username}' created successfully."
    )