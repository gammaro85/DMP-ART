# Security Considerations for DMP-ART

## Important Security Notice

**DMP-ART is designed as a single-user desktop application and should ONLY be run on localhost.**

## Network Security

### Running on Localhost Only

This application should be accessed only via:
- `http://localhost:5000`
- `http://127.0.0.1:5000`

**DO NOT expose this application to the network** without implementing proper authentication and authorization mechanisms.

### Why Localhost Only?

1. **No Authentication**: The application does not implement user authentication
2. **API Keys Storage**: AI API keys are stored in configuration files
3. **File Access**: The application has direct file system access
4. **Configuration Endpoints**: API configuration can be modified through web endpoints

## API Keys and Sensitive Data

### AI Configuration

The `config/ai_config.json` file contains sensitive API keys for:
- OpenAI API
- Anthropic API (Claude)

**Security Measures:**

1. **Gitignore Protection**: `config/ai_config.json` is excluded from version control
2. **Plain Text Warning**: API keys are stored in plain text (acceptable for single-user desktop use)
3. **File Permissions**: Ensure proper file permissions on the config directory

**Best Practices:**

```bash
# Set restrictive permissions on config directory
chmod 700 config/
chmod 600 config/ai_config.json
```

### Environment Variables Alternative

For enhanced security, consider using environment variables instead of the JSON config:

```bash
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

Then modify the code to read from environment variables first, falling back to the config file.

## Input Validation

The application implements input validation for:

1. **File Uploads**: Only PDF and DOCX files accepted
2. **File Size**: Maximum 16MB upload size
3. **Cache IDs**: UUID format validation to prevent path traversal
4. **Filename Sanitization**: Uses `werkzeug.secure_filename()` for uploaded files

## XSS Protection

The application implements HTML escaping for:
- AI-generated suggestions
- User comments
- Template content
- Error messages

All dynamic content rendered in the UI is escaped to prevent cross-site scripting attacks.

## Data Storage

### Uploaded Files

- Stored temporarily in `uploads/` directory
- Automatically cleaned after processing
- Not version-controlled (in `.gitignore`)

### Review Data

- Cached reviews stored in `outputs/cache/`
- Not version-controlled (in `.gitignore`)
- Contains sensitive research proposal information

**Important**: Regularly clean up old cache files containing sensitive data:

```bash
# Clean cache files older than 30 days
find outputs/cache/ -name "cache_*.json" -mtime +30 -delete
```

## Knowledge Base Management

The AI knowledge base (`config/knowledge_base.json`) implements:

1. **Size Limits**: Automatic cleanup of low-usage patterns
2. **Maximum Entries**: 100 entries per section maximum
3. **Age-based Cleanup**: Removes unused patterns older than 90 days
4. **Usage Tracking**: Monitors pattern usage to retain valuable data

## Production Deployment (If Required)

If you must deploy this application in a networked environment:

### Required Security Enhancements

1. **Add Authentication**
   - Implement user login
   - Use Flask-Login or similar
   - Add session management

2. **Use HTTPS**
   - Configure SSL/TLS certificates
   - Use reverse proxy (nginx/Apache)
   - Enforce HTTPS redirects

3. **API Key Management**
   - Move to environment variables
   - Use secrets management service
   - Implement key rotation

4. **Access Control**
   - Implement role-based access
   - Add IP whitelisting
   - Use firewall rules

5. **Rate Limiting**
   - Implement request throttling
   - Prevent API abuse
   - Add CAPTCHA for public forms

### Example Production Setup

```python
# Production configuration example
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Add authentication decorator
from functools import wraps
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# Protect routes
@app.route('/review/<filename>')
@require_auth
def review_page(filename):
    # ... existing code
```

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public GitHub issue
2. Contact the maintainer directly
3. Provide detailed information about the vulnerability
4. Allow time for a fix before public disclosure

## Regular Security Maintenance

### Monthly Tasks

- [ ] Review and rotate API keys
- [ ] Clean up old cache files
- [ ] Check for dependency updates
- [ ] Review access logs (if deployed)

### Dependency Updates

Keep dependencies updated to receive security patches:

```bash
# Check for outdated packages
pip list --outdated

# Update requirements
pip install --upgrade -r requirements.txt
```

### Security Scanning

Run security scanners periodically:

```bash
# Install safety
pip install safety

# Check for known vulnerabilities
safety check -r requirements.txt
```

## Conclusion

DMP-ART is designed for **single-user, localhost operation** where security requirements are minimal. If deploying in a multi-user or networked environment, implement the security enhancements outlined above.

**Remember**: The simplest security measure is to keep the application on localhost and not expose it to the network.
