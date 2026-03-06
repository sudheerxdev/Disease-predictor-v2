# Google OAuth 2.0 Setup Guide

## Overview
This application now supports Google Sign-In/Sign-Up through OAuth 2.0 authentication. Users can log in with their Google account instead of creating a new username and password.

## Features Implemented

### 1. **Backend Authentication Routes**
- `GET /auth/google` - Initiates Google OAuth flow
- `GET /auth/google/callback` - Handles OAuth callback from Google
- Account linking: Users can sign in with email first, then link their Google account
- Automatic username generation for new Google users

### 2. **User Model Enhancements**
- `google_id` field - Stores Google's unique user identifier
- `auth_provider` field - Tracks authentication method ('email' or 'google')
- `from_google()` classmethod - Factory method for creating users from Google OAuth data
- `password_hash` field now nullable for OAuth-only users

### 3. **Frontend UI Updates**
- [Sign In page](backend/templates/auth.html) - Added "Sign in with Google" button
- [Register page](backend/templates/auth.html) - Added "Sign up with Google" button
- Visual divider with "Or continue with" text
- Google branding with official Google logo
- Responsive styling that works on light and dark modes

## Setup Instructions

### Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing one)
3. Enable Google+ API:
   - Go to APIs & Services → Library
   - Search for "Google+ API"
   - Click Enable
4. Create OAuth 2.0 Credentials:
   - Go to APIs & Services → Credentials
   - Click "Create Credentials" → OAuth client ID
   - Application type: **Web application**
   - Add Authorized JavaScript origins:
     - `http://localhost:5000` (development)
     - `http://localhost:5001` (if running on 5001)
     - `http://127.0.0.1:5000`
     - `http://127.0.0.1:5001`
     - Your production domain (e.g., `https://yourdomain.com`)
   - Add Authorized redirect URIs:
     - `http://localhost:5000/auth/google/callback`
     - `http://localhost:5001/auth/google/callback`
     - `http://127.0.0.1:5000/auth/google/callback`
     - `http://127.0.0.1:5001/auth/google/callback`
     - Your production callback (e.g., `https://yourdomain.com/auth/google/callback`)
5. Copy your **Client ID** and **Client Secret**

### Step 2: Configure Environment Variables

Create or edit `.env` file in the project root:

```env
GOOGLE_CLIENT_ID=your_client_id_from_google_cloud.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_from_google_cloud
```

**For Production:**
- Use environment variables or secrets management system
- Never commit `.env` file to version control
- Use `.env.example` template for documentation

### Step 3: Install Required Dependencies

```bash
pip install authlib requests
```

Both packages are already listed in `requirements.txt`.

### Step 4: Start the Application

```bash
python run.py
```

The application will be available at `http://127.0.0.1:5001` (or configured port).

### Step 5: Test Google OAuth Flow

1. Navigate to the authentication page:
   - `http://127.0.0.1:5001/auth`
2. Click **"Sign in with Google"** or **"Sign up with Google"**
3. You'll be redirected to Google's login page
4. Complete authentication with your Google account
5. You'll be automatically logged in and redirected to your profile

## How It Works

### Authentication Flow

```
User clicks "Sign in with Google"
        ↓
/auth/google endpoint called
        ↓
User redirected to Google login
        ↓
User grants permission
        ↓
Google redirects to /auth/google/callback
        ↓
Backend exchanges auth code for user data
        ↓
Check if user exists:
  - If new user: Create account with Google ID
  - If existing email: Link Google account to existing user
  - If existing Google ID: Update user info
        ↓
Auto-login user
        ↓
Redirect to profile/dashboard
```

### Account Linking

Users can authenticate in multiple ways with the same email:
1. **Email/Password → Google**: Create account with email, later sign in with Google
2. **Google → Email/Password**: Sign up with Google, later set password for email login
3. **Both methods**: Use any method to access the same account

## Troubleshooting

### Issue: "Missing or invalid GOOGLE_CLIENT_ID"
**Solution**: 
- Verify `.env` file exists in project root
- Check environment variables are set correctly
- Restart the Flask server after setting `.env`

### Issue: Redirect URI mismatch error
**Solution**:
- The redirect URI in your request must **exactly match** what's configured in Google Cloud Console
- Check for trailing slashes, http vs https, port number
- Make sure you've registered all URIs you'll be using (localhost:5000, 5001, production domain, etc.)

### Issue: User not created/logged in after Google callback
**Solution**:
- Check Flask server logs for errors
- Verify database is working (`sqlite:///disease_predictor.db`)
- Ensure User model includes `google_id` and `auth_provider` fields
- Try deleting test users and restart flow

### Issue: Button not showing in browser
**Solution**:
- Clear browser cache (Ctrl+Shift+Delete)
- Do a hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- Check browser console for JavaScript errors (F12)
- Verify `auth.html` was updated with Google button code

### Issue: 500 error on /auth/google/callback
**Solution**:
- Check that `authlib` is installed: `pip show authlib`
- Verify User model has `google_id` field
- Check Flask logs for specific error message
- Ensure GOOGLE_CLIENT_ID and SECRET are correct

## Files Modified

### Backend Files
- **[backend/models/user.py](backend/models/user.py)** - Added Google OAuth fields and methods
- **[backend/routes/auth_routes.py](backend/routes/auth_routes.py)** - Added OAuth endpoints
- **[backend/utils/google_auth.py](backend/utils/google_auth.py)** - OAuth utility functions (created)

### Frontend Files
- **[backend/templates/auth.html](backend/templates/auth.html)** - Added Google buttons and styling

## Security Considerations

✅ **Implemented:**
- Client secret stored in environment variables (never in code)
- HTTPS redirects to Google's official service
- Server-side token validation
- Account linking validation
- Automatic user creation with strong defaults

⚠️ **For Production:**
- Use HTTPS only (no http://)
- Implement CSRF protection (Flask-WTF)
- Add rate limiting on auth endpoints
- Use secure session cookies
- Implement proper error handling
- Log authentication events
- Regular security audits

## Additional Resources

- [Authlib Documentation](https://docs.authlib.org/en/latest/)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)

## API Reference

### POST /auth/signup (Email/Password)
```bash
curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&email=john@example.com&password=SecurePass123"
```

### POST /auth/login (Email/Password)
```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=john@example.com&password=SecurePass123"
```

### GET /auth/google (Initiate OAuth)
- No body required
- Automatically redirects to Google login

### GET /auth/google/callback (OAuth Callback)
- Automatically handled by Google and backend
- User is logged in and redirected to profile

### GET /auth/logout (Logout)
```bash
curl http://localhost:5001/auth/logout
```

## Future Enhancements

- [ ] Add Microsoft OAuth
- [ ] Add GitHub OAuth
- [ ] Add social provider linking UI
- [ ] Rate limiting on OAuth endpoints
- [ ] Email verification for new Google users
- [ ] Two-factor authentication
- [ ] OAuth scope customization
- [ ] User consent management UI

---

**Last Updated:** March 6, 2026
**Status:** ✅ Ready for Testing
