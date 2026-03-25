from rest_framework import serializers
from .models import IntegracionGitHub, PullRequestSnapshot


class IntegracionGitHubSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegracionGitHub
        fields = ["id", "provider", "owner_repo", "repo_url", "sync_activa", "ultima_sync"]
        read_only_fields = ["id", "ultima_sync"]


class PullRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PullRequestSnapshot
        fields = [
            "id", "pr_number", "titulo", "autor", "estado",
            "rama_origen", "rama_destino", "labels", "url", "updated_at",
        ]
