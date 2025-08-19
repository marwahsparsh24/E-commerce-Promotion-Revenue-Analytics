select
    orders.*,
    orders_item_summary.gross_item_sales_amount,
    orders_item_summary.item_discount_amount
from 
    {{ ref('stg_tpch_orders') }} as orders
join
    {{ ref('int_order_items_summary') }} as orders_item_summary
        on orders.order_key = orders_item_summary.order_key
order by order_date