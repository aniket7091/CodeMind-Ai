def analyze_query(query: str):

    q = query.lower().strip()

    technology = None
    framework = None
    topic = None
    intent = "explanation"

    # =========================================================
    # TECHNOLOGY + FRAMEWORK
    # =========================================================
    #
    # Framework-specific technologies are checked FIRST.
    # This is important because:
    #
    # Python + FastAPI -> technology=fastapi
    # Python + Django  -> technology=django
    # Python + Flask   -> technology=flask
    # Node.js + Express -> technology=nodejs
    #
    # =========================================================

    # Node.js + Express
    if "express" in q:
        technology = "nodejs"
        framework = "express"

    # NestJS
    elif "nestjs" in q or "nest.js" in q:
        technology = "nestjs"
        framework = "nestjs"

    # FastAPI
    elif "fastapi" in q:
        technology = "fastapi"
        framework = "fastapi"

    # Django
    elif "django" in q:
        technology = "django"
        framework = "django"

    # Flask
    elif "flask" in q:
        technology = "flask"
        framework = "flask"

    # Laravel
    elif "laravel" in q:
        technology = "laravel"
        framework = "laravel"

    # Ruby on Rails
    elif "rails" in q or "ruby on rails" in q:
        technology = "rails"
        framework = "rails"

    # React
    elif "react" in q:
        technology = "react"
        framework = "react"

    # Flutter
    elif "flutter" in q:
        technology = "flutter"
        framework = "flutter"

    # .NET
    elif "dotnet" in q or ".net" in q or "asp.net" in q:
        technology = "dotnet"
        framework = "dotnet"

    # Java
    elif "java" in q:
        technology = "java"
        framework = "java"

    # Go
    elif "golang" in q or "go language" in q:
        technology = "go"
        framework = "go"

    # Plain Node.js
    elif any(x in q for x in [
        "node.js",
        "nodejs",
        "node js"
    ]):
        technology = "nodejs"
        framework = "nodejs"

    # Plain Python
    elif "python" in q:
        technology = "python"
        framework = "python"

    # =========================================================
    # TOPICS
    # =========================================================

    topics = []

    # Authentication
    if any(x in q for x in [
        "authentication",
        "authenticate",
        "auth",
        "login",
        "sign in",
        "signin",
        "jwt",
        "oauth",
        "token",
        "session"
    ]):
        topic = "authentication"
        topics.append("authentication")

    # Authorization
    if any(x in q for x in [
        "authorization",
        "authorize",
        "role",
        "roles",
        "permission",
        "permissions",
        "rbac",
        "access control"
    ]):
        topics.append("authorization")

    # Database
    if any(x in q for x in [
        "database",
        "mongodb",
        "mongo",
        "mysql",
        "postgres",
        "postgresql",
        "sql",
        "query",
        "orm"
    ]):
        topics.append("database")

    # API
    if any(x in q for x in [
        "api",
        "rest api",
        "rest",
        "endpoint",
        "http",
        "request",
        "response"
    ]):
        topics.append("api")

    # Routing
    if any(x in q for x in [
        "route",
        "routing",
        "router",
        "url"
    ]):
        topics.append("routing")

    # Security
    if any(x in q for x in [
        "security",
        "secure",
        "csrf",
        "cors",
        "xss",
        "encryption",
        "hashing",
        "password"
    ]):
        topics.append("security")

    # Deployment
    if any(x in q for x in [
        "deploy",
        "deployment",
        "production",
        "hosting",
        "server",
        "docker"
    ]):
        topics.append("deployment")

    # Testing
    if any(x in q for x in [
        "test",
        "testing",
        "unit test",
        "unittest",
        "pytest",
        "jest"
    ]):
        topics.append("testing")

    # =========================================================
    # INTENT
    # =========================================================

    # Code generation
    if any(x in q for x in [
        "code",
        "implement",
        "implementation",
        "example",
        "write",
        "build",
        "create",
        "develop",
        "how do i",
        "how to"
    ]):
        intent = "code_generation"

    # Explanation
    elif any(x in q for x in [
        "what is",
        "what are",
        "explain",
        "meaning",
        "define",
        "why",
        "difference between"
    ]):
        intent = "explanation"

    # =========================================================
    # REMOVE DUPLICATE TOPICS
    # =========================================================

    topics = list(dict.fromkeys(topics))

    # =========================================================
    # RETURN
    # =========================================================

    return {
        "technology": technology,
        "framework": framework,
        "topic": topic,
        "topics": topics,
        "intent": intent
    }