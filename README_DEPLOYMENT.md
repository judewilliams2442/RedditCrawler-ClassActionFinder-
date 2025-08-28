# Reddit Crawler Web Deployment

## Quick Start

1. **Set up environment variables**
   ```
   SECRET_KEY=your_secure_random_key
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

2. **Choose a deployment option**
   - Heroku: Follow the instructions in DEPLOYMENT_GUIDE.md
   - Render: Connect your GitHub repository and deploy
   - PythonAnywhere: Upload your code and configure a web app

3. **Database options**
   - Default: SQLite (works for small deployments)
   - Production: Set `DATABASE_URL` environment variable to use PostgreSQL

## Important Files for Deployment

- `Procfile`: Tells Heroku how to run the application
- `runtime.txt`: Specifies the Python version for Heroku
- `requirements.txt`: Lists all dependencies
- `DEPLOYMENT_GUIDE.md`: Detailed deployment instructions

## Testing Your Deployment

After deploying, verify that:
1. The application loads correctly
2. You can run a crawler job
3. Results are saved to the database
4. Visualizations work properly

## Troubleshooting

If you encounter issues:
1. Check application logs on your hosting platform
2. Verify environment variables are set correctly
3. Ensure database connection is working

For detailed deployment instructions, see `DEPLOYMENT_GUIDE.md`