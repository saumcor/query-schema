# Contributing to *query-schema*

## **Instructions**

### Issues
- Add new requirement/issue/questions in issue tracker of repository.
- Issue(s) raised on repository should preferably have minimum reproducible code
  where ever relevant for others to reproduce and work on issue.

### Pull Requests
- Each PR should have a corresponding issue available in issue tracker of repository.
- To raise a PR, fork **query-schema**
- Clone the project in your local machine
```
git clone https://github.com/saumcor/query-schema.git
cd query-schema
```
- Create a python virtual environment
- Install requirements of project into virtual environment.
- Checkout branch with name relevant to issue issue you are working
```
git checkout -b issue-num
```
- Make changes as per the issue you are working on and add/modify testfile(s) if you are adding
  a new feature or fixing bugs in existing code
- Add commit for your changes with message title and message description brifly explaining the approach
  Follow the commit guidelines at: https://cbea.ms/git-commit/
- Got to github, and raise a PR `saumcor/query-schema:master` and wait for a review.
- Maintainer(s) of the project will review and approve the CI flow to validate changes across different environments.
- If changes are valid and passes all the tests, maintainer(s) will accept the PR(s)
