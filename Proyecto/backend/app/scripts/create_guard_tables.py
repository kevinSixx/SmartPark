from backend.app.database import (
    Base,
    engine,
)

# Importamos AccessEvent porque gate_actions
# tiene una llave foranea hacia access_events.
from backend.app.models.access_event import (
    AccessEvent,
)

from backend.app.models.staff_account import (
    StaffAccount,
)

from backend.app.models.gate_action import (
    GateAction,
)


def main():

    print(
        "[DATABASE] Creando tablas nuevas..."
    )

    Base.metadata.create_all(
        bind=engine,
        tables=[
            StaffAccount.__table__,
            GateAction.__table__,
        ],
    )

    print(
        "[DATABASE] staff_accounts lista."
    )

    print(
        "[DATABASE] gate_actions lista."
    )

    print(
        "[DATABASE] Proceso terminado."
    )


if __name__ == "__main__":
    main()