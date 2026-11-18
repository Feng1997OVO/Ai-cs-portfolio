#开发一个购物车系统，实现商品的增，改，删，查询功能，系统使用嵌套字典结构存储商品数据，
#其功能如下
#（cart,name,price,num)
#1.添加购物车add_xxx 加入商品，已存则累加数量 购物车，名字，价格，数量
#2.修改购物车update_xxx 修改商品 覆盖已有商品的价格和数量 同上
#3.删除购物车商品delete_xxx 删除商品  购物车 名字
#4.查询购物车，将购物车中商品信息展示出来 show_xxx 购物车
#5.退出购物车 谢谢使用

#结构 shopping_cart={"苹果":{"price":10,"num":2},"香蕉":{"price":5,"num":4}}

shopping_cart={}
#1.制作菜单
print("欢迎使用购物车管理系统~！")
menu="""   
##########购物车系统##########
##       1.添加购物车       ##
##       2.修改购物车       ##   
##       3.删除购物车       ##
##       4.查询购物车       ##
##       5.退出购物车       ##
############################
"""

#2.执行具体的操作
def add_item(cart, name, price, num):
    """加入商品。已经存在则累加数量，返回提示语"""
    if name in cart:
        cart[name]["num"] += num
        return f"{name}数量已经累加到{cart[name]['num']}"
    cart[name] = {"price": price, "num": num}
    return f"{name}已经加入购物车"

def delete_item(cart,name):
    """删除商品，不存在则返回提示"""
    if name not in cart:
        return"购物车中没有该商品"
    del cart[name]
    return f"{name}已删除"

def update_item(cart,name,price,num):
    """覆盖已有的商品的价格和数量，不存在则返回提示"""
    if name not in cart:
        return"购物车中没有该商品"
    cart[name]={"price":price,"num":num}
    return f"{name}已修改"

def show_cart(cart):
    """列出所有商品，返回多行文本"""
    if not cart:
        return"购物车是空的"
    lines=[f"{name}|单价{item['price']}|数量{item['num']}"
           for name, item in cart.items()]
    return "\n".join(lines)

def main():
    while True:
        print(menu)
        choice = input("请选择您要执行的操作1-5")

        match choice:
            case "1":       #添加购物车
                name=input("请输入商品的名称")
                price=float(input("请输入商品的价格"))
                num=int(input("请输入商品的数量"))
                print(add_item(shopping_cart,name,price,num))

            case "2":  # 修改购物车
                name = input("请输入要修改商品的名称")
                price = float(input("请输入商品最新的价格"))
                num = int(input("请输入商品最新的数量"))
                print(update_item(shopping_cart,name,price,num))

            case "3":  # 删除购物车
                name = input("请输入要删除商品的名称")
                print(delete_item(shopping_cart,name))
            case "4":  # 查询购物车
                print(show_cart(shopping_cart))
            case "5":  # 退出购物车
                print("再见")
                break
            case _:  # 匹配其他所有情况
                print("输入错误请重新输入")
if __name__=="__main__":
    main()


