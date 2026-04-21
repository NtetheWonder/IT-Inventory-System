import os
import importlib.util
import inspect
import sys


def run_test_file(path):
    spec = importlib.util.spec_from_file_location('testmod', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    tests = [getattr(mod, n) for n in dir(mod) if n.startswith('test_')]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"OK: {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL: {t.__name__} -> {e}")
        except Exception as e:
            failures += 1
            print(f"ERROR: {t.__name__} -> {e}")
    return failures


def main():
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    if not os.path.isdir(tests_dir):
        print('No tests directory found.')
        sys.exit(1)

    total_failures = 0
    for fname in sorted(os.listdir(tests_dir)):
        if fname.startswith('test_') and fname.endswith('.py'):
            path = os.path.join(tests_dir, fname)
            print(f'Running {fname}...')
            total_failures += run_test_file(path)

    if total_failures:
        print(f"{total_failures} tests failed.")
        sys.exit(2)
    print('All tests passed.')


if __name__ == '__main__':
    main()
