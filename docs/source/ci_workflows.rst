.. _ci_workflows:

CI/CD Workflows Tutorial
========================

This tutorial explains the GitHub Actions workflows in this repository, how
and when they run, which tools they use, and how to customize them.

Workflow map
------------

The workflows live under ``.github/workflows/``:

- ``ci.yml``: quality gates (Ruff, ``ty``, lockfile validation, security audit).
- ``test.yml``: runtime validation with a Python matrix and coverage gate.
- ``build.yml``: package build validation with ``python -m build`` + ``twine check``.
- ``docs.yml``: docs build checks for PRs and docs publishing to ``gh-pages``.
- ``uv-env.yml``: dependency-resolution validation with UV extras and Python matrix.
- ``release.yml``: automatic tagging + GitHub Release creation on version bump.
- ``labels.yml``: repository label synchronization from a declarative manifest.

All pull-request-driven workflows include PR lifecycle event types such as
``ready_for_review`` and ``converted_to_draft`` so checks still run when draft
state changes.

Workflow-by-workflow walkthrough
--------------------------------

1) ``ci.yml`` (quality)
~~~~~~~~~~~~~~~~~~~~~~~

This workflow runs on push and pull request events.

It contains four jobs:

- **Ruff**:

  - installs dev dependencies with ``uv sync --frozen --extra dev``;
  - checks formatting with ``uv run ruff format --check .``;
  - checks linting with ``uv run ruff check .``.

- **Ty**:

  - runs static type analysis with ``uv run ty check src/ tests/``.

- **UV lock validation**:

  - verifies the lockfile is up-to-date and consistent using ``uv lock --check``.

- **Security audit**:

  - installs ``pip-audit`` via UV tools;
  - scans installed dependencies for known vulnerabilities.

2) ``test.yml`` (runtime + coverage)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This workflow executes tests across three Python versions:

- ``3.11``
- ``3.12``
- ``3.13``

The test command enforces coverage:

- ``uv run pytest --cov=ditto --cov-report=xml --cov-fail-under=90``

If coverage drops below 90%, the job fails.

3) ``build.yml`` (package validation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This workflow validates packaging correctness:

- installs build tools;
- builds artifacts using ``python -m build``;
- validates generated metadata with ``twine check dist/*``;
- uploads built distributions as CI artifacts.

This catches packaging regressions early without publishing to PyPI.

4) ``docs.yml`` (documentation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This workflow has three responsibilities:

- **PR docs check**: build docs with Sphinx and fail on warnings (``-W``).
- **Main branch deploy**: publish current docs to ``gh-pages``.
- **Release docs deploy**: on GitHub Release publish event, build docs at the
  release tag and publish under a versioned directory (for example ``v0.1.0/``).

This gives you both a "latest" docs site and version-specific docs snapshots.

5) ``uv-env.yml`` (environment validation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This workflow verifies dependency resolution and sync for:

- Python ``3.11``, ``3.12``, ``3.13``;
- extras ``dev`` and ``docs``.

It uses ``uv sync --frozen`` and confirms the package imports successfully.

6) ``release.yml`` (automatic version releases)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This workflow runs on pushes to ``main``.

How it works:

- reads current ``project.version`` from ``pyproject.toml``;
- reads previous commit's ``pyproject.toml`` version;
- compares versions;
- if changed and ``v<version>`` tag does not exist, creates the tag and a
  GitHub Release.

Result: bumping version in ``pyproject.toml`` on ``main`` automatically creates
matching GitHub release metadata.


7) ``labels.yml`` (repository label management)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This workflow keeps repository labels in sync with ``.github/labels.yml``.

How it works:

- runs on manual dispatch, weekly schedule, or when label config changes on ``main``;
- applies labels defined in the manifest using ``micnncim/action-label-syncer``;
- uses ``prune: false`` so missing required labels are added/updated without
  deleting extra labels you may have created manually.

This gives a consistent issue/PR triage taxonomy without requiring manual setup
for every new repository.

Caching and performance
-----------------------

Workflows use:

- ``astral-sh/setup-uv`` with ``enable-cache: true``;
- ``cache-dependency-glob: uv.lock`` to invalidate caches when dependency locks
  change.

This reduces cold-start install time while keeping dependency state reliable.

Common customization options
----------------------------

You can safely adapt these knobs to your project needs:

- **Branch policy**: change ``branches: [main, develop]`` triggers.
- **Coverage gate**: adjust ``--cov-fail-under=90``.
- **Python support window**: update matrix versions.
- **Security strictness**: fail hard or allow warnings for specific CVEs.
- **Release policy**: extend ``release.yml`` to publish artifacts to PyPI.
- **Docs policy**: publish per-tag docs under semantic version aliases like
  ``stable`` and ``latest``.

Troubleshooting tips
--------------------

- If ``uv lock --check`` fails, regenerate lockfile locally and commit it.
- If docs fail on warnings, treat warnings as actionable build errors.
- If release did not trigger, verify:

  - the version changed in ``pyproject.toml``;
  - push target is ``main``;
  - tag ``vX.Y.Z`` does not already exist.

BibTeX references
-----------------

Use the following BibTeX entries in papers or technical documentation that cite
these tools:

.. code-block:: bibtex

   @misc{github_actions,
     title        = {GitHub Actions Documentation},
     howpublished = {\url{https://docs.github.com/actions}},
     year         = {2026}
   }

   @misc{astral_uv,
     title        = {uv: An Extremely Fast Python Package and Project Manager},
     author       = {{Astral}},
     howpublished = {\url{https://docs.astral.sh/uv/}},
     year         = {2026}
   }

   @misc{astral_ruff,
     title        = {Ruff: An Extremely Fast Python Linter and Formatter},
     author       = {{Astral}},
     howpublished = {\url{https://docs.astral.sh/ruff/}},
     year         = {2026}
   }

   @misc{astral_ty,
     title        = {ty: A Python Type Checker},
     author       = {{Astral}},
     howpublished = {\url{https://docs.astral.sh/ty/}},
     year         = {2026}
   }

   @misc{pip_audit,
     title        = {pip-audit: Auditing Python Environments for Known Vulnerabilities},
     howpublished = {\url{https://github.com/pypa/pip-audit}},
     year         = {2026}
   }

   @misc{pytest,
     title        = {pytest Documentation},
     howpublished = {\url{https://docs.pytest.org/}},
     year         = {2026}
   }

   @misc{sphinx,
     title        = {Sphinx Documentation},
     howpublished = {\url{https://www.sphinx-doc.org/}},
     year         = {2026}
   }
