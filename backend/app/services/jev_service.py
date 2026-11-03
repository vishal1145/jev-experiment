import os
import requests


JEV_ENDPOINT = "https://api.typesafe.ai/v1/systemone"

URGENCY_LEVELS = [
    "Very Low",
    "Low",
    "Medium",
    "High",
    "Very High",
    "Critical"
]


class JevServiceError(Exception):
    pass


def analyze_ticket(ticket):
    api_key = os.getenv("TYPESAFE_API_KEY")

    if not api_key:
        raise JevServiceError(
            "TypeSafe API key is missing. Add TYPESAFE_API_KEY "
            "to backend/.env and restart Flask."
        )

    payload = {
        "model": os.getenv("JEV_MODEL", "jev-latest"),

        "state": {
            "ticket": {
                "subject": ticket["subject"],
                "message": ticket["message"]
            }
        },

        "questions": {

            "category": {
                "type": "choice",
                "instructions": (
                    "Choose the best department to handle this "
                    "customer support ticket."
                ),
                "criteria": {
                    "Billing": (
                        "Payments, refunds, invoices or subscriptions"
                    ),
                    "Technical": (
                        "Software bugs, errors or technical problems"
                    ),
                    "Account": (
                        "Login, registration or account access"
                    ),
                    "General": (
                        "General questions and other customer requests"
                    ),
                    "Other": (
                        "The ticket does not fit the other categories"
                    )
                }
            },

            "urgency": {
                "type": "score",
                "instructions": (
                    "Rate the urgency of resolving this support ticket. "
                    "Consider the impact, seriousness and time sensitivity."
                ),
                "criteria": URGENCY_LEVELS
            },

            "human_review": {
                "type": "noul",
                "instructions": (
                    "Does this ticket require a human support agent "
                    "to investigate, review or take action? Consider "
                    "serious complaints, payment problems, account "
                    "problems and unresolved technical issues."
                )
            }
        }
    }

    try:
        response = requests.post(
            JEV_ENDPOINT,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )

        if response.status_code == 401:
            raise JevServiceError(
                "Jev authentication failed. Check your API key."
            )

        if response.status_code == 429:
            raise JevServiceError(
                "Jev rate limit reached. Please try again later."
            )

        response.raise_for_status()
        result = response.json()

        answers = result.get("answers", {})

        category_answer = answers.get("category", {})
        urgency_answer = answers.get("urgency", {})
        review_answer = answers.get("human_review", {})

        if not all([
            category_answer.get("choice"),
            urgency_answer.get("score") is not None,
            review_answer.get("noul") is not None
        ]):
            raise JevServiceError(
                "Jev returned an incomplete decision response."
            )

        category = category_answer["choice"]

        score = max(
            0.0,
            min(5.0, float(urgency_answer["score"]))
        )

        level_index = max(
            0,
            min(5, int(round(score)))
        )

        urgency_label = URGENCY_LEVELS[level_index]

        escalation_probability = max(
            0.0,
            min(1.0, float(review_answer["noul"]))
        )

        threshold = float(
            os.getenv("HUMAN_REVIEW_THRESHOLD", "0.65")
        )

        requires_human_review = (
            escalation_probability >= threshold
        )

        return {
            "category": category,

            "category_confidence": round(
                float(category_answer.get("confidence", 0)),
                3
            ),

            "category_probabilities": (
                category_answer.get("probabilities", {})
            ),

            "urgency_score": round(score, 2),

            "urgency_label": urgency_label,

            "urgency_confidence": round(
                float(urgency_answer.get("confidence", 0)),
                3
            ),

            "urgency_probabilities": (
                urgency_answer.get("probabilities", {})
            ),

            "escalation_probability": round(
                escalation_probability,
                3
            ),

            "requires_human_review": requires_human_review,

            "model": result.get("model", "jev-latest"),

            "usage": result.get("usage", {})
        }

    except requests.Timeout:
        raise JevServiceError(
            "Jev request timed out. Please try again."
        )

    except requests.RequestException as exc:
        raise JevServiceError(
            f"Unable to connect to Jev: {exc}"
        )

    except (ValueError, TypeError, KeyError) as exc:
        raise JevServiceError(
            f"Unable to process Jev response: {exc}"
        )
