"""Registro de todos los blueprints (un módulo por caso de uso)."""


def registrar_blueprints(app):
    from routes.auth import auth_bp
    from routes.calculator import calculator_bp
    from routes.flashcards import flashcards_bp
    from routes.notebook import notebook_bp
    from routes.reminders import reminders_bp
    from routes.schedule import schedule_bp
    from routes.traza import traza_bp

    for bp in (
        auth_bp,
        reminders_bp,
        schedule_bp,
        calculator_bp,
        notebook_bp,
        flashcards_bp,
        traza_bp,
    ):
        app.register_blueprint(bp)
