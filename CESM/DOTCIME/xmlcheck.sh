AC_XMLROOT=${CIMEROOT}/config/xml_schemas
xmllint --noout --schema ${AC_XMLROOT}/config_batch.xsd ./config_batch.xml


xmllint --noout --schema ${AC_XMLROOT}/config_machines.xsd ./config_machines.xml

xmllint --noout --schema ${AC_XMLROOT}/config_compilers_v2.xsd ./config_compilers.xml


