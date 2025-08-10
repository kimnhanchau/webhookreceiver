from flask import Flask, request, jsonify
import requests
import os
import openai  # Optional: only if generating test cases with GPT

app = Flask(__name__)

# OpenAI API key (set in your environment variables)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Jira configuration
JIRA_BASE_URL = "http://localhost:8080/"
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_PROJECT_KEY = "PROJ"


def generate_test_cases(summary, description):
    """Generate test cases from story description using GPT."""
    prompt = f"""
    Generate detailed test cases for the following Jira story:

    Summary: {summary}
    Description: {description}

    Format them in Gherkin style.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # or gpt-4 if you prefer
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def create_jira_test_issue(story_key, test_cases):
    """Create a Test issue in Jira and link it to the Story."""
    url = f"{JIRA_BASE_URL}/rest/api/3/issue"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": f"Test Cases for {story_key}",
            "description": test_cases,
            "issuetype": {"name": "Test"}  # Works if Jira supports "Test" issue type
        }
    }

    response = requests.post(url, json=payload, auth=auth, headers={"Content-Type": "application/json"})
    response.raise_for_status()
    return response.json()


@app.route("/jira-webhook", methods=["POST"])
def jira_webhook():
    print(request.json)
    data = request.json

    issue = data.get("issue", {})
    issue_type = issue.get("fields", {}).get("issuetype", {}).get("name", "")

    # Only process Stories
    if issue_type != "Story":
        return jsonify({"status": "ignored", "reason": "not a Story"}), 200

    story_key = issue.get("key")
    summary = issue.get("fields", {}).get("summary", "")
    description = issue.get("fields", {}).get("description", "")

    # Generate test cases
    # test_cases = generate_test_cases(summary, description)

    # Create Test issue in Jira
    # test_issue = create_jira_test_issue(story_key, test_cases)

    return jsonify({"status": "success", "test_issue": test_issue}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=True)
