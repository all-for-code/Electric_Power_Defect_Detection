#coding=utf-8
#author: lijiang🚀
#data: 2023-12-20🚀
from threading import Thread, Lock
import copy, os
import requests
import json, time
from recognize.rule import mergecls

class OnlineWriter(Thread):
    def __init__(self, state_url, result_url, logging, contestantId=3) -> None:
        super().__init__()
        self.logging = logging
        self._data = list()
        self.state_url = state_url
        self.result_url = result_url
        self.contestantId = contestantId
        self.checkoutNum = 0
        self.faultNum = 0
        self._isEnd = False
        self._mutex = Lock()

    def set_flag(self, checkoutNum, isEnd=False)-> None:
        self._mutex.acquire()
        self.checkoutNum = checkoutNum
        self._isEnd = isEnd
        self._mutex.release()

    def get_flag(self)-> tuple:
        self._mutex.acquire()
        faultNum = self.faultNum
        checkoutNum = self.checkoutNum
        self._mutex.release()
        return checkoutNum, faultNum
    
    def check_end(self)-> bool:
        self._mutex.acquire()
        flag = self._isEnd
        data_flag = False if self._data else True
        self._mutex.release()
        return flag and data_flag

    def send_heart(self)-> bool:
        self._mutex.acquire()
        request_data = {
            "contestantId" : str(self.contestantId),
            "checkoutNum" : self.checkoutNum,
            "faultNum" : self.faultNum
        }
        data = {"state":json.dumps(request_data)}
        self._mutex.release()
        return self.send_message(self.state_url, data)

    def extend(self, results)-> None:
        self._mutex.acquire()
        for result in results:
            self._data.append({
                "id" : result["id"],
                "path" : os.path.basename(str(result["path"])),
                "type" : result["type"] if result["type"] not in mergecls else mergecls[result['type']],
                "score" : result["score"],
                "xmin" : result["xmin"],
                "ymin" : result["ymin"],
                "xmax" : result["xmax"],
                "ymax" : result["ymax"]
            },)
            self.faultNum = result["id"]
        self._mutex.release()

    def pop(self)-> list:
        self._mutex.acquire()
        results = copy.deepcopy(self._data)
        self._data.clear()
        self._mutex.release()
        return results

    def send_message(self, url, json_data)-> bool:
        # headers = {"Content-type": "application/json"}
        response = requests.post(url,
                                 data=json_data)

        status = json.loads(response.text)
        print(status)
        if int(status['statusCode']) == 0:
            return True
        else:
            return False

    def run(self, secs = 10, delay = 0.01):
        while True:
            times = int(secs / delay)
            for i in range(times):
                time.sleep(delay)
                if self.check_end(): # 已经检测完成，提前结束等待时间
                    break
            checkoutNum, faultNum = self.get_flag()
            request_data = {
                "contestantId": str(self.contestantId),
                "checkoutNum": checkoutNum,
                "isEnd" : 1 if self.check_end() else 0,
                "results" : self.pop()
            }
            # 发送心跳
            self.send_heart()
            self.logging.info("发送心跳给服务器")
            self.logging.info(f"checkoutNum:{checkoutNum}")
            self.logging.info(f"faultNum:{faultNum}")
            # 发送检测结果
            if not request_data["results"] and not self.check_end():
                continue 
            data = {"result_text":json.dumps(request_data)}
            self.send_message(self.result_url, data)
            self.logging.info("发送数据给服务器")
            # 检测完成并完成所有信息的发送退出线程
            if self.check_end():
                break