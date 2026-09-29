import re


def detect_metadata(text, technology, source):
    lower = text.lower()

    # -------------------------
    # Framework
    # -------------------------
    if technology == "nodejs":
        if (
            "express.js" in lower
            or "express 5" in lower
            or "from 'express'" in lower
            or 'from "express"' in lower
            or "require('express')" in lower
        ):
            framework = "express"
        else:
            framework = "nodejs"

    elif technology == "nestjs":
        framework = "nestjs"

    elif technology == "django":
        framework = "django"

    elif technology == "flask":
        framework = "flask"

    elif technology == "fastapi":
        framework = "fastapi"

    elif technology == "laravel":
        framework = "laravel"

    elif technology == "rails":
        framework = "rails"

    elif technology == "react":
        framework = "react"

    elif technology == "flutter":
        framework = "flutter"

    elif technology == "dotnet":
        framework = "dotnet"

    elif technology == "go":
        framework = "go"

    elif technology == "java":
        if "spring security" in lower:
            framework = "spring-security"
        elif "spring boot" in lower:
            framework = "spring-boot"
        else:
            framework = "java"

    elif technology == "python":
        framework = "python"

    else:
        framework = technology

    # -------------------------
    # Programming Language
    # -------------------------
    language_map = {
        "nodejs": "javascript",
        "nestjs": "typescript",
        "python": "python",
        "django": "python",
        "flask": "python",
        "fastapi": "python",
        "java": "java",
        "flutter": "dart",
        "react": "javascript",
        "dotnet": "csharp",
        "go": "go",
        "laravel": "php",
        "rails": "ruby",
    }

    language = language_map.get(technology, technology)

    # -------------------------
    # Topics
    # -------------------------
    topic_keywords = {
        "authentication": [
            "authentication",
            "authenticate",
            "login",
            "sign in",
            "jwt",
            "oauth",
            "session",
        ],
        "authorization": [
            "authorization",
            "authorize",
            "permissions",
            "roles",
            "rbac",
        ],
        "routing": [
            "routing",
            "route",
            "router",
            "endpoint",
            "url",
        ],
        "database": [
            "database",
            "sql",
            "mongodb",
            "postgres",
            "mysql",
            "query",
        ],
        "api": [
            "rest api",
            "api",
            "http",
            "request",
            "response",
        ],
        "deployment": [
            "deploy",
            "deployment",
            "production",
            "server",
            "hosting",
        ],
        "testing": [
            "test",
            "testing",
            "unittest",
            "pytest",
            "jest",
        ],
        "security": [
            "security",
            "csrf",
            "cors",
            "xss",
            "encryption",
        ],
    }

    topics = []

    for topic, keywords in topic_keywords.items():
        if any(keyword in lower for keyword in keywords):
            topics.append(topic)

    # -------------------------
    # Content Type
    # -------------------------
    has_code = bool(
        re.search(r"```[\s\S]*?```", text)
    )

    content_type = (
        "code_and_documentation"
        if has_code
        else "documentation"
    )

    return {
        "technology": technology,
        "framework": framework,
        "language": language,
        "topics": topics,
        "content_type": content_type,
        "source": source,
    }