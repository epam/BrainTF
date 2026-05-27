# Contributing to BrAInTF

Thank you for your interest in contributing to the BrAInTF project! We welcome contributions from the community and appreciate your help in making this project better.

## Code of Conduct

By participating in this project, you agree to abide by the principles outlined in our project community. We are committed to providing a welcoming and inclusive environment for all contributors.

## Prerequisites

Before you start contributing, ensure you have the following installed:

| Tool          | Required Version | Notes                                                               |
| ------------- | ---------------- | ------------------------------------------------------------------- |
| **Docker**    | Latest stable    | Used for building and installing Lambda dependencies                |
| **Terraform** | `>= 1.0`.        | See [Terraform releases](https://releases.hashicorp.com/terraform/) |

## Branching Strategy

We follow the **GitHub Flow** branching strategy. This ensures a clean, predictable workflow:

1. The `main` branch is always deployable
2. Create feature branches from `main`
3. Submit pull requests for code review
4. Merge into `main` will be done by maintainers after approval
5. Branches are automatically deleted after merge

## Contribution Workflow

### Step 1: Fork the Repository

We use a **forking strategy** for contributions:

1. Fork the repository to your personal GitHub account
2. Clone your fork locally:

   ```bash
   git clone https://github.com/<your-username>/BrainTF.git
   cd BrainTF
   ```

3. Add the upstream repository as a remote:

   ```bash
   git remote add upstream https://github.com/EPAM/BrainTF.git
   ```

### Step 2: Create an Issue (for most contributions)

Before implementing a significant change, **create an issue** to discuss the reasoning and approach:

- Clearly describe the problem or improvement
- Explain the proposed solution
- Link any relevant issues or discussions

**Exception**: Minor improvements (typos, documentation fixes, small patches) don't require an issue.

### Step 3: Create a Feature Branch

Create a descriptive branch from the latest `main`:

```bash
git fetch upstream
git checkout -b feature/your-feature-name upstream/main
```

Branch naming convention:

- `feature/<description>` for new features
- `fix/<description>` for bug fixes
- `docs/<description>` for documentation updates

### Step 4: Make Your Changes

When making changes:

1. **Write clear, descriptive commits** using [Conventional Commits](https://github.com/commitizen/conventional-commit-types):

   ```
   feat(lambda): add S3 trigger support
   fix(iam): resolve overly permissive policy on role attachment
   feat: add support for X feature
   fix: resolve Y bug in module Z
   docs: update README with new information
   ```

   Format: `<type>(<scope>): <subject>`

2. **Keep commits focused** - each commit should represent a logical change

3. **Update documentation** if your changes affect any docs

4. **Run tests locally**:

   ```bash
   # 1. Format all Terraform files in place
   terraform fmt -recursive .

   # 2. Initialize providers (required before validate)
   terraform init

   # 3. Validate configuration syntax and internal consistency
   terraform validate
   ```

   Ensure all formatting is correct and validation passes before pushing.

### Step 5: Push and Create a Pull Request

Push your branch to your fork:

```bash
git push origin feature/your-feature-name
```

Create a Pull Request (PR) on GitHub against the `main` branch of the original repository:

- Link the related issue (if applicable): "Closes #<issue-number>"
- Provide a clear description of your changes
- Explain the reasoning behind the implementation
- Reference the issue in the PR description

### Step 6: Code Review

Your PR will be reviewed by:

| Reviewer | GitHub ID | Role |
|----------|-----------|------|
| Taras Mazurak | [@mazuraktaras](https://github.com/mazuraktaras) | Maintainer |
| Kateryna Kotova | [@KotovaK](https://github.com/KotovaK) | Maintainer |
| Valerii Mykhailov | [@MykhVal](https://github.com/MykhVal) | Maintainer |

**Requirements before merge**:

- ✅ All CI/CD workflows and checks must pass
- ✅ `terraform fmt` formatting is correct
- ✅ `terraform validate` passes
- ✅ Code review approval from at least one maintainer
- ✅ Documentation is updated (if applicable)

### Step 7: Merge

When your PR is approved:

1. All commits will be **squashed into a single commit** during merge
2. The branch will be **automatically deleted** after merge
3. The commit message will be based on the PR title

## Local Development

### Setup

1. Clone your forked repository
2. Ensure Docker and Terraform v1.latest are installed
3. Navigate to the relevant terraform directory
4. Review the specific README.md in each module for additional setup details

### Testing

Before submitting your PR, run:

```bash
# 1. Format all Terraform files in place
terraform fmt -recursive .

# 2. Initialize providers (required before validate)
terraform init

# 3. Validate configuration syntax and internal consistency
terraform validate
```

Ensure there are no errors or warnings.

## Documentation

- If your changes modify functionality or add new features, update the relevant README.md files
- Keep documentation clear and up-to-date
- Include examples where applicable

## License

By contributing to BrAInTF, you agree to license your contributions under the terms of the existing [LICENSE](./LICENSE) file. You do not need to sign a CLA; your contribution constitutes agreement to these terms.

## Getting Help

If you have questions or need clarification:

- Open an issue with your question
- Reach out to the maintainers
- Check existing issues and documentation first

## Thank You!

Thank you for contributing to BrAInTF. Your efforts help make this project better for everyone!
