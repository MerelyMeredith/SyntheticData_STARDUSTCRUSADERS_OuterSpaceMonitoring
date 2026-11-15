"""Future modular scripts, one file per CLI command.

Each module must expose::

    def run(context) -> int: ...

See ``app.core.registry`` for the ``Context`` definition. Planned modules:
``configure``, ``generate``, ``validate`` and ``preview``.
"""
