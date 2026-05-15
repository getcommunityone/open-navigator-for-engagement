{% macro jurisdiction_acs_exists() %}
  {% set rel = adapter.get_relation(
      database=target.database,
      schema='public',
      identifier='jurisdiction_acs'
  ) %}
  {{ return(rel is not none) }}
{% endmacro %}
