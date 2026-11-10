# Configuration with intentional security flaws for Code Intelligence Studio detection

# Leaked AWS Credentials (CRITICAL Severity)
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Leaked AI Provider Token (CRITICAL Severity)
OPENAI_API_KEY = "sk-live1234567890abcdefghijklmnopqrstuvwxyz123456"

# Hardcoded Database Password
DB_PASSWORD = "SuperSecretProductionDatabasePassword2026!"
DB_URI = f"postgresql://admin:{DB_PASSWORD}@production-db.internal:5432/payments"
