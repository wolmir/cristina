echo '' > pytest.log
py.test --ignore=tests/test_data -vv -l -x --timeout=300 -r a --full-trace
