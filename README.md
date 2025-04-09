# Story Generation & Video Creation with GitHub Actions

This repository contains a Python script (`cd.py`) that generates children's stories, images, and videos using Google's Gemini AI model. The script is configured to run automatically via GitHub Actions.

## Files in this Repository

- **cd.py** - The main script that generates stories, images, and videos using Google's Gemini AI model
- **main.py** - A wrapper script designed specifically for GitHub Actions that handles environment setup and compatibility issues
- **requirements.txt** - Contains all the necessary Python dependencies
- **.github/workflows/run_cd_script.yml** - GitHub Actions workflow configuration

## Setup Instructions

Follow these steps to configure the GitHub Actions workflow:

### 1. Fork this repository

Fork or clone this repository to your own GitHub account.

### 2. Set up repository secrets

You need to add two secrets to your GitHub repository:

1. **GEMINI_API_KEY** - Your Google Gemini API key
2. **GOOGLE_DRIVE_CREDENTIALS** - Your Google Drive API credentials JSON file content

To add these secrets:
- Go to your repository on GitHub
- Click on "Settings" > "Secrets and variables" > "Actions"
- Click "New repository secret"
- Add each secret with the appropriate name and value

### Getting a Gemini API Key

1. Visit the [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an account if you don't have one
3. Generate an API key
4. Copy the key and add it as the `GEMINI_API_KEY` secret

### Getting Google Drive Credentials

1. Visit the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Drive API
4. Create a service account with appropriate permissions
5. Generate and download a JSON key for the service account
6. Copy the entire contents of the JSON file and add it as the `GOOGLE_DRIVE_CREDENTIALS` secret

## Running the Workflow

The workflow can be triggered in two ways:

1. **Manually**: Go to the "Actions" tab in your repository, select the "Run CD Script" workflow, and click "Run workflow"
2. **Automatically**: The workflow is scheduled to run daily at midnight UTC

When the workflow runs, it will:
1. Set up the required Python environment and dependencies
2. Create a temporary directory for outputs
3. Execute main.py, which wraps cd.py with proper GitHub Actions compatibility
4. Upload all generated files as artifacts

## Workflow Output

After the workflow runs, it will:

1. Generate a children's story using the Gemini AI model
2. Create images for each scene in the story
3. Generate audio narration
4. Create a video combining the images and audio
5. Upload the video and metadata to Google Drive (if configured)

The generated files will be available as artifacts in the workflow run, which you can download from the Actions tab.

## How it Works

The repository is structured to run efficiently in GitHub Actions:

1. **main.py** handles GitHub Actions specific setup:
   - Creates appropriate temporary directories
   - Provides mock implementations of IPython display functions
   - Sets up the environment for cd.py to run properly

2. **cd.py** contains the core functionality:
   - Connecting to Google's Gemini API
   - Generating story content
   - Creating images, audio, and video

3. **GitHub Actions Workflow**:
   - Installs all dependencies from requirements.txt
   - Runs main.py instead of directly running cd.py
   - Collects and stores all generated outputs

## Customization

You can customize the workflow by modifying:

- The schedule in `.github/workflows/run_cd_script.yml`
- The script parameters in `cd.py` (e.g., changing prompt settings)

## Troubleshooting

If the workflow fails:

1. Check the workflow logs for error messages
2. Verify your API keys and credentials are correct
3. Ensure all required secrets are properly set
4. Check that you have sufficient quota/credits for the Gemini API

## Notes

- The script requires significant API calls, which may incur costs depending on your API usage tier
- Video generation can be resource-intensive and may occasionally fail on GitHub Actions due to memory limitations
