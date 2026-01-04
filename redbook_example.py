import requests  
import json  
import base64  
from PIL import Image  
import io  

class XiaohongshuMCPClient:  
    def __init__(self, base_url="http://localhost:18060"):  
        self.base_url = base_url  
        self.api_base = f"{base_url}/api/v1"  
      
    def _call(self, method, endpoint, data=None):  
        """内部API调用方法"""  
        url = f"{self.api_base}/{endpoint}"  
        headers = {"Content-Type": "application/json"}  
          
        if method.upper() == "GET":  
            response = requests.get(url, headers=headers)  
        elif method.upper() == "POST":  
            response = requests.post(url, headers=headers, json=data)  
          
        return response.json()  
      
    def health_check(self):  
        """健康检查"""  
        return requests.get(f"{self.base_url}/health").json()  
      
    def check_login(self):  
        """检查登录状态"""  
        return self._call("GET", "login/status")  
      
    def publish_post(self, title, content, images):  
        """发布图文"""  
        data = {"title": title, "content": content, "images": images}  
        return self._call("POST", "publish", data)  
      
    def search_content(self, keyword):  
        """搜索内容"""  
        data = {"keyword": keyword}  
        return self._call("POST", "search", data)  
  
# 使用示例  
if __name__ == "__main__":  
    client = XiaohongshuMCPClient()  
      
    # 检查服务状态  
    health = client.health_check()  
    print(f"服务状态: {health['data']['status']}")  
      
    # 检查登录状态  
    login = client.check_login()  
    if login['data']['is_logged_in']:  
        print("已登录，可以发布内容")  
          
        # 发布内容  
        result = client.publish_post(  
            title="随便发一个",  
            content="发个图试试",  
            images=[f"./output/20251231162524/images_20251231163228_0.png"]   # https://oss.agnet.top/keep/2025/12/31/20251231173649991.png
        )  
        print(result)
        print(f"发布结果: {result['success']}")  
    else:  
        print("请先登录小红书账号")
            # 解码并显示二维码  

        response = requests.get("http://localhost:18060/api/v1/login/qrcode")  
        data = response.json()  
        img_data = base64.b64decode(data['data']['img'].replace('data:image/png;base64,', ''))  
        img = Image.open(io.BytesIO(img_data))  
        img.show()  
        
        print(f"请在 {data['data']['timeout']} 内扫码登录")