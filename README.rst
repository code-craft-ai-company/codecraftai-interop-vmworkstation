==============================================
Code Craft AI Interop - VMware Workstation
==============================================

The ``codecraftai-interop-vmworkstation`` package is a typed, aspect-driven client for VMware Workstation that drives the local ``vmrun`` CLI tool. Unlike its sibling ``codecraftai-interop-vsphere``, this package does **not** build on ``RestClientBase`` — Workstation has no REST API. Instead it uses ``ICommandRunner`` from ``codecraftai-foundations`` to dispatch ``vmrun`` argv tuples and parse the textual output.

The package replaces the legacy ``VMWorkstationAgent`` that lived under ``codecraftai-landscaping/services/vmware/``.

Highlights
==========

- ``VMWorkstationClient`` — the top-level client that exposes lifecycle, snapshot, and guest-exec operations through a single ``ICommandRunner``-driven dispatcher.
- Lifecycle: ``start``, ``stop``, ``suspend``, ``reset`` — each idempotent via state probes through ``vmrun list``.
- Snapshots: ``snapshot_create``, ``snapshot_revert``, ``snapshot_delete``, ``snapshot_list`` (parses ``vmrun listSnapshots`` into ``SnapshotRecord``).
- Guest exec via VMware Tools: ``run_program_in_guest``, ``copy_file_to_guest``, ``copy_file_from_guest``, ``tools_state``.
- Inventory: ``list_running`` parses ``vmrun list`` into a list of open VMX paths.
- ``AspectsVMWorkstation`` extends the generic ``Aspects`` with ``dry_run``, ``elevated``, ``command_timeout``, and ``raise_on_failure``.
- Same package works locally (via ``LocalCommandRunner``) and remotely (via ``SSHCommandRunner``) without any client-side changes.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/ccai/interop/vmworkstation/`` - Package source code.
- ``source/testroots/testbase/ccai/tests/interop/vmworkstation/`` - TestBase test roots.
- ``specs/`` - Requirements, design, and task documentation (Kiro-style).
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-environment

Running Tests
=============

Activate the virtual environment:

.. code-block:: bash

   source .venv/bin/activate

Run the test suite:

.. code-block:: bash

   testbase testing run --root ./source/testroots/testbase --includes=testbase.ccai.tests
Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``
