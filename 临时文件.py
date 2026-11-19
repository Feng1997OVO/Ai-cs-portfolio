import json

CART_FILE="cart.json"

def save_cart(cart,path=CART_FILE):
    """把购物车写进文件里"""
    with open(path,'w',encoding="utf-8") as f:
        json.dump(cart,f,ensure_ascii=False,indent=2)

def load_cart(path=CART_FILE):
    """从文件读取购物车。文件如果不存在就返回空字典。"""
    try:
        with open(path,'r',encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
