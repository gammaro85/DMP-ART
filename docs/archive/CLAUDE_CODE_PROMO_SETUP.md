# Claude Code Promo Credits Setup Guide

## 🎉 Promotional Credits Offer

**IMPORTANT: This promotion ends TODAY - November 18, 2025 at 11:59 PM PT**

Anthropic is offering promotional credits for Claude Code on the web:
- **Claude Pro subscribers**: $250 in credits
- **Claude Max subscribers**: $1000 in credits

## ✅ Configuration Complete

This repository has been configured to use your Claude Pro/Max promotional credits with Claude Code VSCode CLI. The configuration includes:

### 1. VSCode Settings (`.vscode/settings.json`)

The following Claude Code settings have been added:
```json
{
  "claude-code.apiEndpoint": "https://api.anthropic.com",
  "claude-code.environmentVariables": {
    "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
    "ANTHROPIC_MODEL": "claude-sonnet-4-5-20250929"
  },
  "claude-code.telemetry.enabled": false
}
```

### 2. Claude Code Settings (`.claude/settings.local.json`)

The following settings force Claude Code to use your Claude.ai account:
```json
{
  "forceLoginMethod": "claudeai",
  "model": "claude-sonnet-4-5-20250929",
  "includeCoAuthoredBy": true
}
```

## 📋 How to Claim Your Promo Credits

### Step 1: Verify Your Subscription
1. Visit [claude.ai](https://claude.ai)
2. Ensure you have an active **Claude Pro** or **Claude Max** subscription
3. If you don't have a subscription, upgrade before the promotion ends!

### Step 2: Claim Your Credits
1. Log in to your Claude account at [claude.ai](https://claude.ai)
2. Navigate to the promotional credits page (check your email for the direct link)
3. **Alternative**: Visit the support article at: https://support.claude.com/en/articles/12690958-claude-code-promotion
4. Click "Claim Credits" or follow the instructions provided
5. Credits will be automatically added to your account

### Step 3: Authenticate Claude Code
1. Open this project in VSCode
2. Open the Command Palette (`Ctrl+Shift+P` on Windows/Linux, `Cmd+Shift+P` on Mac)
3. Type "Claude Code: Sign In" and select it
4. Choose **"Sign in with Claude.ai"** (NOT Console)
5. Follow the browser authentication flow
6. Authorize VSCode to use your Claude account

### Step 4: Verify Configuration
1. In VSCode, open a new Claude Code chat
2. Check that you're using the Sonnet 4.5 model
3. Your promo credits will now be used for Claude Code operations

## 🔧 Configuration Details

### `forceLoginMethod: "claudeai"`
This setting ensures that Claude Code uses your Claude.ai account (where your Pro/Max subscription and promo credits are) instead of the Console API billing.

### `model: "claude-sonnet-4-5-20250929"`
This specifies the exact Claude Sonnet 4.5 model to use, which is the latest and most capable model available.

### API Endpoint Configuration
The VSCode settings point to the official Anthropic API endpoint (`https://api.anthropic.com`), ensuring that requests are properly authenticated and charged against your promotional credits.

## 💡 How to Use Your Credits

Once configured, your promotional credits will automatically be used for:

- **Chat interactions** in Claude Code
- **Code generation** and refactoring
- **File analysis** and understanding
- **Terminal command** suggestions
- **Git operations** assistance
- **Documentation** generation
- **Bug fixing** and debugging

## 📊 Monitoring Credit Usage

To check your remaining promotional credits:

1. Visit [claude.ai](https://claude.ai)
2. Go to your account settings
3. Navigate to "Usage" or "Billing"
4. View your promotional credit balance

## ⚠️ Important Notes

### Credit Expiration
- **Claim by**: November 18, 2025 at 11:59 PM PT
- **Usage period**: Check the promotion terms for expiration date
- Credits typically expire within 30-90 days after claiming

### Subscription Requirement
- You MUST maintain an active Claude Pro or Max subscription
- If you cancel your subscription, you may lose access to unclaimed credits

### Usage Priority
- Promotional credits are typically used BEFORE your subscription allowance
- This helps you maximize the value of your promotion

### Credit Limits
- Pro subscribers: $250 total
- Max subscribers: $1000 total
- No additional credits after the initial claim
- Standard rate limits apply

## 🛠️ Troubleshooting

### Problem: "Authentication Failed"
**Solution**:
1. Sign out of Claude Code: `Ctrl+Shift+P` → "Claude Code: Sign Out"
2. Clear authentication cache: Delete `~/.claude/claude.json` (backup first!)
3. Sign in again with "Claude.ai" option

### Problem: "Credits Not Being Used"
**Solution**:
1. Verify `forceLoginMethod` is set to `"claudeai"` in `.claude/settings.local.json`
2. Ensure you're signed in to the correct Claude.ai account
3. Check your credit balance on claude.ai to confirm credits were claimed

### Problem: "Using Console Billing Instead"
**Solution**:
1. Check that `.claude/settings.local.json` has `"forceLoginMethod": "claudeai"`
2. Sign out and sign back in
3. When signing in, explicitly choose "Claude.ai" NOT "Console"

### Problem: "Model Not Available"
**Solution**:
1. Verify your subscription tier includes access to Claude Sonnet 4.5
2. Check for any service outages at https://status.anthropic.com
3. Try switching to a different model temporarily

## 📚 Additional Resources

- **Claude Code Documentation**: https://code.claude.com/docs
- **Claude.ai Dashboard**: https://claude.ai
- **Anthropic Status Page**: https://status.anthropic.com
- **Support**: https://support.anthropic.com

## 🚀 Quick Start Commands

After setup, try these commands in Claude Code:

```plaintext
# In VSCode, open Claude Code and try:
"Explain the architecture of this project"
"Help me refactor the app.py file"
"Write tests for the DMPExtractor class"
"Review my code for security issues"
"Generate documentation for the utils module"
```

## 📝 Configuration Files Modified

The following files were created/modified for this setup:

1. **`.vscode/settings.json`** - VSCode workspace settings with Claude Code API configuration
2. **`.claude/settings.local.json`** - Claude Code settings for authentication and model selection
3. **`CLAUDE_CODE_PROMO_SETUP.md`** - This documentation file

## 🎯 Next Steps

1. ✅ Configuration is complete
2. ⏰ **Claim your promo credits TODAY** (promotion ends November 18, 2025)
3. 🔐 Authenticate Claude Code with your Claude.ai account
4. 🚀 Start using Claude Code with your promotional credits!

---

**Last Updated**: November 18, 2025
**Configuration Version**: 1.0
**Claude Code Version**: 2.0+
