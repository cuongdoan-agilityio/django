from rest_framework import serializers

from polls.models import Poll, Question


class QuestionSerializer(serializers.ModelSerializer[Question]):
    """Question serializer"""

    class Meta:
        model = Question
        fields = ["question_text", "pub_date"]


class PollSerializer(serializers.ModelSerializer[Poll]):
    """Poll serializer"""

    questions = QuestionSerializer(many=True, source="question_set")

    class Meta:
        model = Poll
        fields = ["name", "description", "questions"]
