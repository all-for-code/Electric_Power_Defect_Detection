#coding=utf-8
#author: lijiang🚀
#data: 2023-12-20🚀

import os,shutil
import sys, torch
import argparse
import torchvision.transforms as transforms
import cv2 as cv
from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import time
import numpy as np
import copy
from ultralytics.data.build import load_inference_source
from ultralytics import YOLO
from torchvision.ops import nms
from PIL import Image, ImageDraw, ImageFont
if sys.version_info[0] == 2:
    import xml.etree.cElementTree as ET
else:
    import xml.etree.ElementTree as ET
from recognize.eval_batch_new import eval_batch
from recognize.rule import *
from recognize.client import OnlineWriter
import posixpath
import os
import logging

# 设置日志级别和输出格式
logging.basicConfig(filename='/home/ubuntu/09_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MyDataset(Dataset):
    def __init__(self, imgsz, img_path):
        super(MyDataset, self).__init__()
        self.imgsz = imgsz
        self.root = img_path
        # 传入的为图片的路径，路径下不存在其他非图片文件
        if os.path.isdir(img_path):
            images = os.listdir(img_path)
            # 过滤掉以"."开头的隐藏文件
            self.img = [Path(img_path).joinpath(image) for image in images \
                        if not image.startswith(".") and Path(image).suffix == '.jpg']
        # 传入的为txt文件
        elif Path(img_path).suffix ==  ".txt": # 兼容北京的比赛接口
            with open(img_path) as file:
                lines = file.readlines()
                folder = Path(img_path).parent
                self.img = [folder.joinpath(line.strip()) for line in lines \
                            if Path(line.strip()).suffix == '.jpg']
        else:
            raise RuntimeError(f"img_path should be a path of file or folder")

        self.transform = transforms.Compose([
                         transforms.Resize([imgsz,imgsz]),
                         transforms.ToTensor()
                         ])
    
    def get_imgs(self):
        return self.img

    def __len__(self):
        return len(self.img)

    def __getitem__(self, item):
        try:
            img = self.img[item]
            img = Image.open(img).convert('RGB')
            width, height = img.size
            origin_size = np.array([width, height])
            origin_size = torch.from_numpy(origin_size)
            if self.transform is not None:
                img = self.transform(img)
            return img, origin_size
        except: # 过滤掉无法读取的文件
            img = torch.zeros((3,self.imgsz,self.imgsz))
            origin_size = torch.tensor([self.imgsz,self.imgsz])
            return img, origin_size

class Inference():
    def __init__(self, **kwargs):
        logging.info('开始推理')
        self.imgsz = kwargs['imgsz']
        self.bs = kwargs['bs']
        self.imgpth = kwargs['imgpth']
        self.wpth = kwargs['wpth']
        self.xmlpth = kwargs['xmlpth']
        self.nw = kwargs['nw']
        self.stpth = kwargs['stpth']
        self.stfile = kwargs['stfile']
        self.saveimgpth = kwargs['saveimgpth']
        self.model = YOLO(self.wpth)
        self.stateurl = kwargs['stateurl']
        self.resulturl = kwargs['resulturl']
        self.id = kwargs['cid']
        self.verbose = kwargs['verbose']
        self.resultcsv = kwargs['resultcsv']
        self.dataset = MyDataset(self.imgsz, self.imgpth)
        self.dataloader = DataLoader(dataset = self.dataset, 
                                     batch_size = self.bs,
                                     num_workers = self.nw, 
                                     drop_last = False, 
                                     shuffle = False, 
                                     pin_memory = True)
        self.imgs_pth = self.dataset.get_imgs()
        self.dataloader_length = len(self.dataloader)
        self.server = None
        if self.stateurl and self.resulturl:
            self.server = OnlineWriter(self.stateurl, self.resulturl, logging, self.id)

    def __call__(self):
        # 记录当前检测的图片数量
        imgnum = 1
        # 记录当前缺陷的数量
        faultnum = 1
        # 记录所有图片的检测信息
        result_all_img = list()
        # result = list()
        # 启动发送服务器
        if self.server:
            self.server.start() 
        for index, (data, origin_size) in enumerate(self.dataloader):
            origin_shape = data.shape[0]
            if index == self.dataloader_length - 1:
                data_new = torch.zeros([self.bs,3,self.imgsz,self.imgsz])
                data_new[:data.shape[0],:,:,:] = data
                data = data_new
            outputs = self.model.predict(source = data,
                                         imgsz = self.imgsz, 
                                         half = True, 
                                         iou = 0.15,
                                         conf = 0.15,
                                         agnostic_nms = False,
                                         augment = True,
                                         verbose = self.verbose)  # source already setup
            outputs = outputs[:origin_shape]
            # t2 = time.time()
            # 遍历所有图片的检测结果，其中output为一个batch图片的检测结果
            for batch_index, output in enumerate(outputs):
                result_per_img = list() # 一张图片的检测结果
                result_units = list()   # 一张图片中部件的检测结果
                result_flaws = list()   # 一张图片中缺陷的检测结果
                result_slys = list()    # 一张图片中sly的检测结果
                lastnum = faultnum
                # 遍历一个batch图片的检测结果
                for box in output.boxes:
                    result = dict()
                    name = output.names[int(box.cls)]
                    if name not in allcls:
                        continue
                    width, height = origin_size[batch_index]
                    xmin, ymin, xmax, ymax = box.cpu().xyxy[0].numpy()
                    result["id"] = faultnum
                    result['imgnum'] = imgnum
                    result["path"] = self.imgs_pth[imgnum - 1]
                    result["type"] = name
                    result["score"] = round(float(box.conf),4)
                    # 置信度过滤
                    if result["score"] < conf[result['type']]:
                        continue
                    xmin = int(xmin * origin_size[batch_index][0] / self.imgsz)
                    xmax = int(xmax * origin_size[batch_index][0] / self.imgsz)
                    ymin = int(ymin * origin_size[batch_index][1] / self.imgsz)
                    ymax = int(ymax * origin_size[batch_index][1] / self.imgsz)
                    result["xmin"] = max(xmin, 0)
                    result["ymin"] = max(ymin, 0)
                    result["xmax"] = min(xmax, int(width))
                    result["ymax"] = min(ymax, int(height))
                    # 需要注意的是：对于sly_bjbmyw标签，需要先进行过滤才能进行绑定输出
                    if name in filtercls:
                        result_slys.append(result)
                    elif name in bindingcls.keys():
                        result_flaws.append(result)
                    elif name in unitcls:
                        result_units.append(result)
                    else:
                        result_per_img.append(result)
                    faultnum = faultnum + 1
                # 对sly标签进行过滤操作
                sly_bjbmyw, sly_dmyw = self.filter_cls(result_slys)
                # 添加过滤后的sly标签
                result_per_img.extend(sly_dmyw)
                result_flaws.extend(sly_bjbmyw)
                # 缺陷标签和部件标签进行绑定
                self.bind_cls(result_flaws, result_units)
                # 添加缺陷标签和部件标签绑定后的标签
                result_per_img.extend(result_flaws)
                # 发送服务器添加结果
                if self.server:
                    # 由于对部分检测到的标签进行了删减，所以需要重新对id进行修正排序
                    faultnum = self.reorder_id(result_per_img, lastnum)
                    self.server.extend(result_per_img)
                    self.server.set_flag(checkoutNum=imgnum, isEnd=False)
                # 写入一个图片的检测结果，两种模式，如果是stfile模式，所有结果写入同一个txt文件中；
                # 如果是stpth模式，单个图片检测结果写入与图片名同名的txt文件中
                if self.stpth:
                    txt = Path(os.path.basename(self.imgs_pth[imgnum - 1])).with_suffix(".txt")
                    save_txt = Path(self.stpth).joinpath(txt)
                    self.write_sorted_txt(result_per_img, save_txt)
                if self.saveimgpth or self.stfile:
                    result_all_img.extend(result_per_img)
                imgnum = imgnum + 1
        # 所有图片检测完成，通知发送线程退出线程
        if self.server:
            self.server.set_flag(imgnum-1, True)
        if self.stfile:
            logging.info('保存结果到txt')
            self.write_sorted_txt(result_all_img, self.stfile)
        # 计算pr
        if self.xmlpth:
            if self.stfile:
                eval_batch(self.xmlpth, self.stfile, outputcls, self.resultcsv)
            if self.stpth:
                eval_batch(self.xmlpth, self.stpth, outputcls, self.resultcsv)
        # 原图上绘制boxes
        if self.saveimgpth:
            self.draw_anchor(result_all_img, self.saveimgpth)
        # 最好是放在最后，防止服务器出现卡顿，导致主进程长时间等待
        if self.server:
            self.server.join()
        logging.info('推理结束')
        open('/home/ubuntu/09.ok', 'w').close()

    def truncation_list(self, results, num = 10, reverse = True):
        if len(results) <= 10:
            return results
        else:
            results = sorted(results, key=lambda x: x['score'], reverse=reverse)
            return results[0:10]
        

    def reorder_id(self, results: list, start: int)-> int:
        """
        根据已检测到的缺陷的数量对当前图片的检测结果进行id的重新排序
        Args:
            results: 单个图片的检测到的所有结果，包括缺陷和标签
        Return:
            start: id的起始值
        """
        for result in results:
            result['id'] = start
            start = start + 1
        return start

    def filter_cls(self, results: list)-> tuple:
        """
        用于过滤掉sly_bjbmyw,sly_dmyw中重叠包含的标签
        Args:
            results: 单个图片的sly_bjbmyw,sly_dmyw缺陷标签
        Return:
            sly_bjbmyw: 过滤后的sly_bjbmyw结果
            sly_dmyw: 过滤后的sly_dmyw结果
        """
        sly_flag = [False for sly in results]
        for index1, result1 in enumerate(results):
            for result2 in results:
                if result1 == result2 or result1['type'] != result2['type']:
                    continue
                if self.check_is_included(result1, result2):
                    sly_flag[index1] = True
        # 得到被删减后的sly_bjbmyw结果
        sly_bjbmyw = [results[i] for i in range(len(results)) if not sly_flag[i] and results[i]['type'] == "sly_bjbmyw"] 
        # 得到被删减后的sly_dmyw结果
        sly_dmyw = [results[i] for i in range(len(results)) if not sly_flag[i] and results[i]['type'] == "sly_dmyw"] 
        return sly_bjbmyw, sly_dmyw
        
    def bind_cls(self, result_flaws: list, result_units: list)-> None:
        """
        用于将缺陷标签和部件标签进行绑定输出, 规则为检测到缺陷标签才判断是否输出设备
        Args:
            result_flaws: 单个图片的缺陷标签
            result_units: 单个图片的部件标签
        Return:
            None
        """
        units = list()
        for flaw in result_flaws:
            # 如果部件标签只有一种且属于未标注的标签，只需要修改标签为部件标签直接输出即可
            if len(bindingcls[flaw['type']]) == 1 and bindingcls[flaw['type']][0] in ununitcls:
                result = copy.deepcopy(flaw)    # 需要拷贝一份，防止修改原有的缺陷标签
                result['type'] = bindingcls[flaw['type']][0]
                units.append(result)
                continue
            for unit in result_units:
                # 是否添加部件标签，还需要保证部件标签只添加一次
                if unit['type'] in bindingcls[flaw['type']] and unit not in units:
                    box1 = [flaw['xmin'],flaw['ymin'],flaw['xmax'],flaw['ymax']]
                    box2 = [unit['xmin'],unit['ymin'],unit['xmax'],unit['ymax']]
                    if self.calculate_iou(box1, box2) > float(bindingiou[flaw['type']]):
                        units.append(unit)
        result_flaws.extend(units)

    def check_is_included(self, result1: dict, result2: dict)-> bool:
        """
        用于检查result1中的box是否被result2中的box包含其中
        Args:
            results1: 图片中某一个检测框的检测结果信息
            results2: 图片中某一个检测框的检测结果信息
        Return:
            bool
        """
        box1 = [result1['xmin'], result1['ymin'], result1['xmax'], result1['ymax']]
        box2 = [result2['xmin'], result2['ymin'], result2['xmax'], result2['ymax']]
        if box1[0] >= box2[0] and box1[1] >= box2[1] and box1[2] <= box2[2] and box1[3] <= box2[3]:
            return True
        else:
            return False

    def write_sorted_txt(self, results: list, save_txt:str, reverse = True)-> None:
        """
        将一张图片的检测结果根据result['score']进行排序，并
        Args:
            results: 所有图片的检测结果，格式为: [result,...]
            save_txt: 写入的txt文件路径
            reverse: 排序的方式，逆序和顺序
        Return:
            None
        """
        if results:
            results = sorted(results, key=lambda x: x['score'], reverse=reverse)
            for index, result in enumerate(results):
                result['id'] = index + 1
        self.write_one_txt(results, save_txt)

    def write_one_txt(self, results: list, save_txt:str):
        """
        将一张图片的检测结果写入txt文件中
        Args:
            results: 所有图片的检测结果，格式为: [result,...]
            save_txt: 写入的txt文件路径
        Return:
            None
        """
        if not os.path.exists(os.path.dirname(save_txt)):
            os.makedirs(os.path.dirname(save_txt))
        if os.path.exists(save_txt):
            model = 'a'
        else:
            model = 'w'
        try:
            with open(save_txt, model) as f:
                if model == 'w':
                    title = "ID,PATH,TYPE,SCORE,XMIN,YMIN,XMAX,YMAX"
                    f.write(title + '\n')
                for index, box in enumerate(results):
                    filename = os.path.basename(box['path'])
                    typename = box['type']
                    score = box['score']
                    xmin = box['xmin']
                    xmax = box['xmax']
                    ymin = box['ymin']
                    ymax = box['ymax']
                    if typename in mergecls.keys():
                        typename = mergecls[typename]
                    content = f"{index+1},{filename},{typename},{score},{xmin},{ymin},{xmax},{ymax}"
                    f.write(content + '\n')
                f.close()
        except Exception as e:
            print(e)
            print(f"{save_txt}文件写入失败")

    def calculate_iou(self, box1: list, box2: list)-> float:
        """
        计算两个box的iou, box1,box2均为xyxy
        Args:
            box1: 图片的中某个box的坐标列表，格式为: [xmin, ymin, xmax, ymax]
            box2: 图片的中某个box的坐标列表
        Return:
            iou: 返回两个box的iou值
        """
        inter_x1 = max(box1[0], box2[0])
        inter_y1 = max(box1[1], box2[1])
        inter_x2 = min(box1[2], box2[2])
        inter_y2 = min(box1[3], box2[3])
        # +1 是为了处理边界框重叠的情况
        inter_area = max(0, inter_x2 - inter_x1 + 1) * max(0, inter_y2 - inter_y1 + 1)

        box1_area = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
        box2_area = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area

    def draw_anchor(self, results: list, save_pth: str):
        """
        在检测到的图片上绘制检测框并保存
        Args:
            results: 检测到的所有图片的检测结果，格式为: {"imgpth": results,...}
            save_pth: 保存绘制图片的路径
        Return:
            None
        """
        # 没有检测道任何一个标签, 直接返回
        if not results:
            return
        if not os.path.exists(save_pth):
            os.makedirs(save_pth)
        result_all_img = dict()
        # list转dict
        for result in results:
            if result["path"] not in result_all_img.keys():
                result_all_img[result["path"]] = list()
            result_all_img[result["path"]].append(result)
        for key, boxes in result_all_img.items():
            if not boxes:
                continue
            orig_img = cv.imread(str(key))
            height = orig_img.shape[0]
            width = orig_img.shape[1]
            orig_img = cv.cvtColor(orig_img, cv.COLOR_RGB2BGR)
            img_pth = key
            for box in boxes:
                x1, y1, x2, y2 = box['xmin'], box['ymin'], box['xmax'], box['ymax']
                cv.rectangle(orig_img, (x1,y1), (x2,y2), (255,0,0), 6)
                text = str(box['type']) + " " + str(box['score'])
                text_org = (x1, int(y1) + 30)
                cv.putText(orig_img, text, text_org, cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, bottomLeftOrigin=False)
            cv.imwrite(os.path.join(save_pth, os.path.basename(img_pth)), orig_img[:,:,[2,1,0]])
