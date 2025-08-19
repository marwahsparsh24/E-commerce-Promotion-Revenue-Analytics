{% macro discounted_amount(extended_price, discount_pct, scale=2) %}
    (-1 * {{extended_price}} * {{discount_pct}})::decimal(16, {{ scale }})
{% endmacro %}