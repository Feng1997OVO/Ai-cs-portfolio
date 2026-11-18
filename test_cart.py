from cart import add_item, update_item, delete_item, show_cart

cart = {}
print(add_item(cart, "苹果", 10, 2))     # 苹果已经加入购物车
print(add_item(cart, "苹果", 10, 3))     # 苹果数量已经累加到 5
print(update_item(cart, "苹果", 12, 5))  # 苹果已修改
print(show_cart(cart))                   # 苹果|单价12|数量5
print(delete_item(cart, "苹果"))         # 苹果已删除
print(show_cart(cart))                   # 购物车是空的