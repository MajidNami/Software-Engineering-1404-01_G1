from django.conf import settings

class TeamPerAppRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label in settings.TEAM_APPS:
            return model._meta.app_label
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in settings.TEAM_APPS:
            return model._meta.app_label
        return None

    def allow_relation(self, obj1, obj2, **hints):
        db1 = self.db_for_read(obj1.__class__) if hasattr(obj1, '_meta') else None
        db2 = self.db_for_read(obj2.__class__) if hasattr(obj2, '_meta') else None

        if db1 is None or db2 is None:
            return None

        return db1 == db2

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in settings.TEAM_APPS:
            return db == app_label
        return None