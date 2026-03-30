# Wordastra - Full-Stack Blog Platform

A modern, full-featured blog platform built with Django, PostgreSQL, and Clerk authentication.

## 🚀 Features

- **User Authentication**: Clerk integration with multiple login options (Google, Email, etc.)
- **Blog Management**: Full CRUD operations for blog posts
- **Rich Text Editor**: TinyMCE integration for writing blogs
- **Comments System**: Authenticated users can comment on blogs
- **Like/Unlike**: Users can like blog posts and comments
- **User Dashboard**: Track your blogs, views, likes, and session info
- **Admin Panel**: Full admin control over users and posts
- **Responsive Design**: Bootstrap 5 with modern UI
- **Session Tracking**: Active session monitoring with timestamps
- **Search Functionality**: Search blogs by title and content
- **REST API**: Django REST Framework endpoints
- **Health Check**: `/health/` endpoint for monitoring
- **Production Ready**: Configured for Render and Vercel deployment

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL (local or cloud)
- Clerk account for authentication

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd blog
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

**Activate virtual environment:**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables Setup

Create a `.env` file in the root directory:

```bash
# Django Settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/wordastra

# Clerk Authentication
CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
CLERK_SECRET_KEY=sk_test_your_secret_key_here
CLERK_FRONTEND_API=your-frontend-api.clerk.accounts.dev

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### 5. Database Setup

**For Local PostgreSQL:**
1. Install PostgreSQL
2. Create a database named `wordastra`
3. Update `DATABASE_URL` in `.env` with your credentials

**For Cloud PostgreSQL (Recommended for Production):**
- Use services like Neon.tech, Supabase, or Render's managed PostgreSQL
- Get the connection URL and set it as `DATABASE_URL`

### 6. Clerk Setup

1. Sign up at https://clerk.com
2. Create a new application
3. Enable authentication methods (Email, Google, etc.)
4. Copy your API keys from the dashboard
5. Add keys to `.env` file
6. Update the Clerk script URL in `templates/users/login.html` with your Frontend API

### 7. Run Migrations

```bash
python manage.py migrate
```

### 8. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 9. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the blog.

## 🚀 Deployment

The app is configured for deployment on Render and Vercel with PostgreSQL support.

### Environment Variables for Production

Set these in your deployment platform:

```
SECRET_KEY=your-very-long-random-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,your-app.onrender.com,your-app.vercel.app
DATABASE_URL=postgresql://user:pass@host:port/dbname
CLERK_PUBLISHABLE_KEY=your-clerk-key
CLERK_SECRET_KEY=your-clerk-secret
CLERK_FRONTEND_API=your-clerk-api
```

### Render Deployment

1. Connect your GitHub repo to Render
2. Create a PostgreSQL database
3. Create a Web Service with:
   - **Runtime**: Python 3.11.5
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput --clear && python manage.py migrate`
   - **Start Command**: `gunicorn wordastra.wsgi:application --bind 0.0.0.0:$PORT`
4. Set environment variables
5. Deploy

**Keep App Awake**: Use UptimeRobot (free) to ping `https://your-app.onrender.com/health/` every 5 minutes.

### Vercel Deployment

1. Install Vercel CLI: `npm install -g vercel`
2. Run `vercel` and connect your repo
3. Set environment variables in Vercel dashboard
4. Deploy (auto-deploys on push)

Vercel is serverless and stays awake automatically.

### Post-Deployment

- Run `python manage.py createsuperuser` via shell if needed
- Test the `/health/` endpoint
- Configure custom domain if desired

## 📁 Project Structure

```
blog/
├── blogs/                 # Blog app
├── users/                 # User management app
├── wordastra/            # Project settings
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS)
├── media/                # User uploaded files
├── api/                  # Vercel serverless functions
├── requirements.txt      # Python dependencies
├── manage.py            # Django management script
├── vercel.json          # Vercel configuration
└── README.md            # This file
```

## 🔧 API Endpoints

- `GET /` - Home page with blog list
- `GET /health/` - Health check endpoint
- `POST /blogs/api/posts/` - Create blog post (API)
- `GET /blogs/api/posts/` - List blog posts (API)
- Authentication handled via Clerk

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter issues:
1. Check the `/health/` endpoint
2. Verify environment variables
3. Ensure database is accessible
4. Check logs in deployment platform

For questions, open an issue on GitHub.

### 9. Create Superuser

```bash
python manage.py createsuperuser
```

### 10. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 11. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## 📁 Project Structure

```
blog/
├── wordastra/              # Main project directory
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   ├── wsgi.py             # WSGI configuration
│   ├── users/              # Users app
│   │   ├── models.py       # User model
│   │   ├── views.py        # User views
│   │   ├── middleware.py   # Clerk authentication middleware
│   │   └── admin.py        # User admin
│   ├── blogs/              # Blogs app
│   │   ├── models.py       # Blog and Comment models
│   │   ├── views.py        # Blog views
│   │   ├── forms.py        # Blog forms
│   │   ├── serializers.py  # REST API serializers
│   │   └── admin.py        # Blog admin
│   ├── templates/          # HTML templates
│   │   ├── base.html       # Base template
│   │   ├── blogs/          # Blog templates
│   │   └── users/          # User templates
│   └── static/             # Static files
│       ├── css/            # CSS files
│       └── js/             # JavaScript files
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── Procfile                # Render deployment
├── runtime.txt             # Python version
├── .env.example            # Environment variables example
└── README.md               # This file
```

## 🎨 Admin Panel

Access the admin panel at: http://127.0.0.1:8000/admin

**Admin Features:**
- Manage all users (CRUD operations)
- Manage all blog posts (CRUD operations)
- View comments
- Monitor user sessions
- View statistics

## 🔐 Authentication Flow

1. User clicks "Login" button
2. Clerk authentication modal appears
3. User signs in with email, Google, or other methods
4. Clerk middleware validates the session
5. User is automatically created/logged in Django
6. Session tracking begins

## 📱 User Features

### For Guests:
- Browse all published blogs
- Read blog posts
- Search blogs
- View blog statistics (views, likes, comments)

### For Authenticated Users:
- All guest features
- Write and publish blog posts
- Edit/delete own blog posts
- Like/unlike blogs
- Comment on blogs
- Delete own comments
- Access personal dashboard
- View profile with session info

### For Admins:
- All user features
- Edit/delete any blog post
- Delete any comment
- Manage users via admin panel
- View all statistics

## 🚀 Deployment on Render

### 1. Prepare for Deployment

Ensure these files exist:
- `requirements.txt`
- `Procfile`
- `runtime.txt`

### 2. Update Settings for Production

In `wordastra/settings.py`, update:

```python
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='your-app.onrender.com').split(',')
```

### 3. Create Render Account

1. Sign up at https://render.com
2. Connect your GitHub repository

### 4. Create Web Service

1. Click "New +" → "Web Service"
2. Connect your repository
3. Configure:
   - **Name**: wordastra
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wordastra.wsgi:application`

### 5. Add Environment Variables

In Render dashboard, add all variables from `.env`:
- SECRET_KEY
- DEBUG=False
- ALLOWED_HOSTS=your-app.onrender.com
- MONGODB_URI
- CLERK_PUBLISHABLE_KEY
- CLERK_SECRET_KEY
- CLERK_FRONTEND_API

### 6. Deploy

Click "Create Web Service" and wait for deployment.

### 7. Run Migrations

In Render shell:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## 🔧 API Endpoints

### REST API

- `GET /api/blogs/` - List all blogs
- `POST /api/blogs/` - Create blog (authenticated)
- `GET /api/blogs/{id}/` - Get blog details
- `PUT /api/blogs/{id}/` - Update blog (authenticated)
- `DELETE /api/blogs/{id}/` - Delete blog (authenticated)

## 🐛 Troubleshooting

### MongoDB Connection Issues
- Verify connection string in `.env`
- Check IP whitelist in MongoDB Atlas
- Ensure database user has correct permissions

### Clerk Authentication Not Working
- Verify API keys in `.env`
- Update Frontend API URL in login template
- Check Clerk dashboard for application status

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Check STATIC_ROOT and STATIC_URL in settings
- Ensure WhiteNoise is installed

### Migration Errors
- Delete migration files (except `__init__.py`)
- Run `python manage.py makemigrations`
- Run `python manage.py migrate`

## 📝 Usage Guide

### Creating a Blog Post

1. Login to your account
2. Click "Write Blog" in navbar
3. Enter title and content
4. Use rich text editor for formatting
5. Check "Publish immediately" or save as draft
6. Click "Create Blog"

### Managing Your Blogs

1. Go to Dashboard
2. View all your blogs with statistics
3. Edit, view, or delete blogs
4. Track views, likes, and comments

## 🤝 Contributing

This is a beginner-friendly project. Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

This project is open-source and available under the MIT License.

## 👨‍💻 Author

Built with ❤️ for the Django community

## 🙏 Acknowledgments

- Django Framework
- MongoDB
- Clerk Authentication
- Bootstrap
- TinyMCE
- Font Awesome

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review Django documentation
- Check Clerk documentation
- Open an issue on GitHub

---

**Happy Blogging! 🎉**
