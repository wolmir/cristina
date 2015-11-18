echo '' > pytest.log
py.test --ignore=tests/test_data -vv -l -x --timeout=1200 -r a --full-trace
