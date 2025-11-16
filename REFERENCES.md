# References

Quick reference guide for common commands and operations.

## Initial Steps

1. Create the environment file:

   ```bash
   touch .env
   ```

2. Add the debug flag inside `.env`:

   ```bash
   DEBUG=True
   ```

## How to Run Dockerfile

**Create and start a container**

```bash
docker build -t autopilot-os .
docker run -it -v $(pwd):/autopilot-os --env-file .env autopilot-os bash
```

## Extra Docker Commands

- List Docker images

  ```bash
  docker images
  ```

- Run the container by name

  ```bash
  docker run -it --name autopilot-os autopilot-os /bin/bash
  ```

- Remove an image

  ```bash
  docker rmi <container-id>
  ```

## Git Commands

**Clone and initialize**

```bash
git clone https://github.com/yourusername/reponame.git
cd reponame
git add .
git commit -m "Initial commit"
git push origin main
```

**Remove file from GitHub repo**

```bash
git rm -r --cached <filename>
git add .
git commit -m "Removed <filename> from repo"
git pull
git push
```

**Create and push a feature branch**

```bash
git checkout -b feature/your-branch-name
git add .
git commit -m "Describe your changes"
git push origin feature/your-branch-name
```

**Open a pull request (from GitHub UI)**

1. Navigate to the repository on GitHub.
2. You should see a banner for your recently pushed branch—click "Compare & pull request."
3. Fill in the PR details and click "Create pull request."

**Checkout an existing branch**

```bash
git fetch origin
git checkout feature/your-branch-name
```

**Merge a branch into main**

```bash
git checkout main
git pull origin main
git merge feature/your-branch-name
git push origin main
```

