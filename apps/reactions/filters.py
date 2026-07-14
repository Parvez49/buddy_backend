import django_filters

from apps.reactions.choices import ReactionType


class ReactionFilter(django_filters.FilterSet):
    reaction_type = django_filters.ChoiceFilter(choices=ReactionType.choices)
