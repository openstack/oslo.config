========================================
 ConfigOpts state and spawn processes
========================================

The ``spawn`` multiprocessing start method starts a fresh Python interpreter.
Unlike a process created with ``fork``, the child does not inherit the parent
process memory state.  A configured :class:`~oslo_config.cfg.ConfigOpts`
instance can be passed to a spawned worker because it supports Python
``pickle`` serialization.

The :meth:`~oslo_config.cfg.ConfigOpts.export_state` method returns an explicit
snapshot, and :meth:`~oslo_config.cfg.ConfigOpts.import_state` creates a new
``ConfigOpts`` instance from such a snapshot.  Pickling a ``ConfigOpts``
instance uses the same snapshot representation.

The snapshot preserves registered options and groups, parsed command-line and
configuration-file values, defaults, overrides, parsed namespaces, and setup
metadata such as the project name and default configuration files and
directories.

Process-local state is intentionally not serialized.  This includes argparse
parsers, caches, mutation hooks, extension managers, and environment drivers.
The child recreates the internal objects needed for normal option access, but
applications must register mutation hooks again and recreate any other
process-local state that they need in the child.

Alternative configuration sources
---------------------------------

A snapshot cannot be exported after alternative configuration sources have
been loaded.  These sources are typically created when the ``config_source``
option or ``--config_source`` command-line argument is used, and may contain
process-local or non-picklable resources.  In that case, serialization raises
:class:`~oslo_config.cfg.ConfigOptsSerializationError` rather than silently
discarding configuration state.  Driver option metadata associated with
configuration source drivers is also unsupported.

Applications that use alternative sources should pass serializable inputs to
the child and recreate the sources there instead of passing the configured
``ConfigOpts`` instance.

Using ConfigOpts with multiprocessing spawn
-------------------------------------------

Worker functions must be defined at module scope so that ``spawn`` can import
them.  In this example, the override set in the parent is available in the
child:

.. code-block:: python

   import multiprocessing

   from oslo_config import cfg


   def worker(conf, result_queue):
       result_queue.put(conf.worker_count)


   if __name__ == '__main__':
       conf = cfg.ConfigOpts()
       conf.register_opt(cfg.IntOpt('worker_count', default=1))
       conf.set_override('worker_count', 4)

       context = multiprocessing.get_context('spawn')
       result_queue = context.Queue()
       process = context.Process(target=worker, args=(conf, result_queue))
       process.start()

       assert result_queue.get() == 4
       process.join()
       assert process.exitcode == 0

