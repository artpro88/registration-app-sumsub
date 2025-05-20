# GitHub Deployment Instructions

Follow these step-by-step instructions to deploy your registration app to GitHub.

## Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in to your account
2. Click the "+" icon in the top right corner and select "New repository"
3. Enter "registration-app-sumsub" as the repository name
4. Add a description: "Registration App with Sumsub Identity Verification"
5. Choose "Public" visibility
6. Check "Add a README file"
7. Click "Create repository"

## Step 2: Push Your Code to GitHub

Run these commands in your terminal:

```bash
# Add the GitHub repository as a remote
git remote add origin https://github.com/YOUR_USERNAME/registration-app-sumsub.git

# Push your code to GitHub
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 3: Set Up GitHub Actions Secrets

1. Go to your repository on GitHub
2. Click on "Settings" tab
3. Click on "Secrets and variables" in the left sidebar
4. Click on "Actions"
5. Click "New repository secret"
6. Add the following secrets one by one:

   a. Name: `DOCKERHUB_USERNAME`
      Value: Your Docker Hub username
   
   b. Name: `DOCKERHUB_TOKEN`
      Value: Your Docker Hub token/password
   
   c. Name: `SUMSUB_APP_TOKEN`
      Value: sbx:KLRZP8PRbxeNmlgfpMzyiDRY.Qqjq7MWF2nJAzjxvUR9zEK6BZkE04MqX
   
   d. Name: `SUMSUB_SECRET_KEY`
      Value: 0YIkTYFr1Xex1402bqIn9Gw6658s0sq9

## Step 4: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click on "Settings" tab
3. Click on "Pages" in the left sidebar
4. Under "Source", select "GitHub Actions"
5. Wait for the GitHub Pages workflow to run
6. Once completed, you'll see a message with your site URL

## Step 5: Update API URL in Frontend (if needed)

If you've deployed your backend to a different URL, update the API URL in `frontend/public/simple.html`:

1. Find the API URL configuration:
   ```javascript
   const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
     ? 'http://localhost:8080/api'
     : 'https://api.registration-app.yourdomain.com/api';
   ```

2. Replace `'https://api.registration-app.yourdomain.com/api'` with your actual backend URL

3. Commit and push the changes:
   ```bash
   git add frontend/public/simple.html
   git commit -m "Update API URL for production"
   git push origin main
   ```

## Step 6: Test the Deployed Application

1. Visit your GitHub Pages URL: `https://YOUR_USERNAME.github.io/registration-app-sumsub/`
2. Test the registration flow
3. Verify that the session expiration issue is fixed

## Troubleshooting

If you encounter any issues:

1. Check GitHub Actions tab for any workflow failures
2. Ensure your repository is public
3. Verify that your GitHub token has the necessary permissions
4. Check browser console for any JavaScript errors
