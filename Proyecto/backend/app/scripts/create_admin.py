from getpass import getpass

from sqlalchemy import select

from backend.app.database import (
    SessionLocal,
)

from backend.app.models.staff_account import (
    StaffAccount,
)

from backend.app.schemas.staff_account import (
    StaffAccountCreate,
)

from backend.app.services.staff_accounts import (
    create_staff_account,
)


def main():

    print()
    print("=" * 60)
    print("SMARTPARK UCE - CREAR ADMINISTRADOR")
    print("=" * 60)
    print()

    full_name = input(
        "Nombre completo: "
    ).strip()

    username = input(
        "Usuario: "
    ).strip().lower()

    password = getpass(
        "Contraseña: "
    )

    password_confirm = getpass(
        "Confirmar contraseña: "
    )

    if password != password_confirm:

        print()
        print(
            "[ERROR] Las contraseñas no coinciden."
        )

        return

    if len(password) < 6:

        print()
        print(
            "[ERROR] La contraseña debe tener "
            "al menos 6 caracteres."
        )

        return

    db = SessionLocal()

    try:

        existing = db.scalar(
            select(
                StaffAccount
            ).where(
                StaffAccount.username
                == username
            )
        )

        if existing is not None:

            print()
            print(
                f"[ERROR] El usuario "
                f"'{username}' ya existe."
            )

            return

        admin_data = StaffAccountCreate(
            full_name=full_name,
            username=username,
            password=password,
            role="ADMIN",
            active=True,
        )

        admin = create_staff_account(
            db,
            admin_data,
        )

        print()
        print("=" * 60)
        print("ADMINISTRADOR CREADO CORRECTAMENTE")
        print("=" * 60)
        print(
            f"ID: {admin.id}"
        )
        print(
            f"Nombre: {admin.full_name}"
        )
        print(
            f"Usuario: {admin.username}"
        )
        print(
            f"Rol: {admin.role}"
        )
        print(
            f"Activo: {admin.active}"
        )
        print("=" * 60)

    finally:

        db.close()


if __name__ == "__main__":
    main()