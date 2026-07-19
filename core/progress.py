from __future__ import annotations

from collections.abc import Callable
from multiprocessing import get_context


ProgressCallback = Callable[[int, int], None]
_worker_progress_counter = None
_POLL_INTERVAL_SECONDS = 0.1


def map_with_progress(worker, tasks: list, process_count: int, total: int, progress_callback: ProgressCallback | None = None):
    """执行多进程 map，并在主进程中定期汇报已完成数量。"""
    context = get_context()
    if progress_callback is None:
        with context.Pool(processes=process_count) as pool:
            return pool.map(worker, tasks)

    progress_callback(0, total)
    progress_counter = context.Value("q", 0)
    pool = context.Pool(processes=process_count, initializer=_initialize_worker_progress, initargs=(progress_counter,))
    completed = 0

    try:
        async_result = pool.map_async(worker, tasks)
        while not async_result.ready():
            async_result.wait(_POLL_INTERVAL_SECONDS)
            new_completed = progress_counter.value
            if new_completed != completed:
                completed = new_completed
                progress_callback(min(completed, total), total)
        results = async_result.get()
    except Exception:
        pool.terminate()
        raise
    else:
        pool.close()
    finally:
        pool.join()

    if completed != total:
        progress_callback(total, total)
    return results


def report_worker_progress(count: int = 1) -> None:
    if _worker_progress_counter is not None:
        with _worker_progress_counter.get_lock():
            _worker_progress_counter.value += count


def _initialize_worker_progress(progress_counter) -> None:
    global _worker_progress_counter
    _worker_progress_counter = progress_counter
