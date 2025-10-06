curl -X POST "http://localhost:8983/solr/admin/cores" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "action=CREATE" \
  --data-urlencode "name=smoke_test_v1" \
  --data-urlencode "instanceDir=smoke_test_v1" \
  --data-urlencode "configSet=_default"