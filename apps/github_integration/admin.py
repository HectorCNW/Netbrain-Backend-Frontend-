from django.contrib import admin
from .models import IntegracionGitHub, PullRequestSnapshot

@admin.register(IntegracionGitHub)
class IntegracionAdmin(admin.ModelAdmin):
    list_display = ["proyecto", "owner_repo", "sync_activa", "ultima_sync"]

@admin.register(PullRequestSnapshot)
class PRAdmin(admin.ModelAdmin):
    list_display = ["pr_number", "titulo", "autor", "estado", "updated_at"]
    list_filter = ["estado"]
