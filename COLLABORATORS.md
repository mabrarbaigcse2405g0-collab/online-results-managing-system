# Project Collaborators & DevOps Git Workflow Log

## 👥 Collaborators Added
1. **Akshith Mucharla**
   - **GitHub Profile:** [Akshith155](https://github.com/Akshith155)
   - **Email:** `akshithmucharla@gmail.com`
   - **Role:** Collaborator / Feature Developer / Pull Request Sender
   - **Contributions:** Implemented Student Registration Form (`student_register.html`), registration field validation, and Result Feedback Feed portal (`feedback.html`) adapted from [Akshith155/akshith159](https://github.com/Akshith155/akshith159) and [Akshith155/Akshith](https://github.com/Akshith155/Akshith).

2. **Amogh**
   - **Affiliation:** MGIT CSE
   - **Email:** `amogh_cse@mgit.ac.in`
   - **Role:** Collaborator / Code Reviewer & Pull Request Approver / Merger
   - **Contributions:** Code review of the feature branch `feed-registration-feature`, verification of automated unit tests, approval, and merging of PR #8 into `main`.

---

## 🔄 DevOps Collaborative Git Workflow

```
[Akshith's System]
   |
   +--> git checkout -b feed-registration-feature
   +--> Develop Student Registration & Feedback Feature
   +--> git commit (Author: Akshith Mucharla)
   +--> git push origin feed-registration-feature
   |
   v
[GitHub Repository: mabrarbaigcse2405g0-collab/online-results-managing-system]
   |
   +--> Pull Request #8 opened by Akshith
   |
   v
[Amogh's System (Reviewer)]
   |
   +--> Review PR #8 diff and test suite (35 tests passing)
   +--> Approve changes
   +--> Merge Pull Request #8 into main
   +--> git push origin main
   |
   v
[Jenkins CI/CD Automation (Port 8080)]
   |
   +--> SCM Polling detects commit on refs/heads/main
   +--> Triggers Build #15 for job 'online-results-managing-system'
   +--> Runs automated test pipeline & deployment
   +--> Status: SUCCESS
```
