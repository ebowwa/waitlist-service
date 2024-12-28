from setuptools import setup, find_namespace_packages

setup(
    name="waitlist-service",
    version="0.1.0",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "pydantic",
        "python-dotenv",
        "databases",
        "supabase",
        "aiosqlite",  # Required for SQLite async support
        "asyncpg",    # Required for PostgreSQL async support
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-asyncio",
        ],
    },
)
