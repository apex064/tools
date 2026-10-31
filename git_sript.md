Installation
chmod +x create-repo.sh
sudo mv create-repo.sh /usr/local/bin/create-repo


Usage
Create a public repository:
create-repo tools public


Create a private repository:
create-repo my-project private


Interactive mode:
create-repo


It will ask for the repository name and visibility.
What it handles
- Checks Git and GitHub CLI authentication.
- Initializes Git if necessary.
- Switches the branch to main.
- Stages and commits project files.
- Creates the GitHub repository.
- Configures the remote.
- Pushes to GitHub.
- Handles existing origin remotes with confirmation.
Requirement: Have GitHub CLI installed and authenticated using gh auth login.
