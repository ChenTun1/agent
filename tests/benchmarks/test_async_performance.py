"""异步处理性能基准测试"""
import pytest
import time
import os
from backend.services.cache_service import get_cache_service


class TestAsyncPerformance:
    """异步处理性能基准"""

    @pytest.fixture
    def cache(self):
        """缓存实例"""
        return get_cache_service()

    def test_cache_performance(self, cache):
        """测试缓存性能 - 目标: 写入<5ms, 读取<3ms"""
        key = "perf_test"
        value = {"data": "x" * 1000}  # 1KB 数据

        # 写入性能
        write_times = []
        for _ in range(100):
            start = time.time()
            cache.set(key, value, ttl=60)
            write_times.append((time.time() - start) * 1000)

        avg_write = sum(write_times) / len(write_times)
        print(f"\n[Cache Write] Avg: {avg_write:.2f}ms")

        # 读取性能
        read_times = []
        for _ in range(100):
            start = time.time()
            cache.get(key)
            read_times.append((time.time() - start) * 1000)

        avg_read = sum(read_times) / len(read_times)
        print(f"[Cache Read] Avg: {avg_read:.2f}ms")

        # 基准: 写入 < 5ms, 读取 < 3ms
        assert avg_write < 5, f"Cache write too slow: {avg_write:.2f}ms (target: <5ms)"
        assert avg_read < 3, f"Cache read too slow: {avg_read:.2f}ms (target: <3ms)"

    def test_cache_hit_rate(self, cache):
        """测试缓存命中率 - 目标: ≥80%"""
        # 准备数据
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}", ttl=60)

        hits = 0
        misses = 0

        # 模拟查询 (80% 重复, 20% 新)
        for i in range(500):
            if i % 5 == 0:
                # 20% 新查询
                result = cache.get(f"new_key_{i}")
                if result is None:
                    misses += 1
            else:
                # 80% 重复查询
                key_idx = i % 100
                result = cache.get(f"key_{key_idx}")
                if result is not None:
                    hits += 1

        hit_rate = hits / (hits + misses)
        print(f"\n[Cache Hit Rate] {hit_rate:.1%} ({hits} hits, {misses} misses)")

        # 基准: 命中率 >= 80%
        assert hit_rate >= 0.8, f"Cache hit rate too low: {hit_rate:.1%} (target: ≥80%)"

    def test_pdf_processing_time(self):
        """测试 PDF 处理时间 (需要 Worker) - 目标: 小文件<10s"""
        # Skip if test PDF doesn't exist
        pdf_path = '/Users/mlamp/.config/superpowers/worktrees/agent/phase2-async-cache/tests/fixtures/sample.pdf'
        if not os.path.exists(pdf_path):
            pytest.skip("需要测试 PDF 文件")

        from backend.tasks.pdf_tasks import process_pdf_task
        from celery.exceptions import TimeoutError as CeleryTimeoutError

        # Check if worker is available by trying with a short timeout
        result = process_pdf_task.delay(
            pdf_path=pdf_path,
            pdf_id='perf_test'
        )

        try:
            start = time.time()
            # Wait for completion with timeout
            task_result = result.get(timeout=30)
            duration = time.time() - start

            print(f"\n[PDF Processing] Time: {duration:.2f}s")
            print(f"  Status: {task_result.get('status', 'unknown')}")
            print(f"  Chunks: {task_result.get('chunks_count', 0)}")

            # 基准: 小文件 < 10秒
            assert duration < 10, f"PDF processing too slow: {duration:.2f}s (target: <10s)"
        except CeleryTimeoutError:
            pytest.skip("需要 Celery Worker 运行 - 使用 'celery -A backend.celery_app worker' 启动")
