#coding=utf-8
#author: lijiang🚀
#data: 2023-10-20🚀
import os, shutil
from pathlib import Path
from xml.etree import ElementTree as ET
import numpy as np
import csv

detect_dict = {
    "sly_bjbmyw": "部件表面油污",
    "sly_dmyw": "地面油污",
    "hxq_gjbs": "硅胶变色",
    "ywzt_yfyc": "油位状态异常",
    "hxq_gjtps": "硅胶桶破损",
    "hxq_yfps": "呼吸器油封破损",
    "hxq_yfzc": "呼吸器油封正常",
    "cysb_cyg": "储油设备_储油柜",
    "cysb_sgz": "储油设备_升高座",
    "cysb_tg": "储油设备_套管",
    "cysb_lqq": "储油设备_冷却器",
    "cysb_qyb": "储油设备_潜油泵",
    "cysb_qtjdq": "储油设备_气体继电器",
    "ylsff": "压力释放阀",
    "pzq": "膨胀器",
    "pzqcd": "膨胀器冲顶",
    "jyh": "均压环",
    "jyhbx": "均压环变形",
    "drq": "电容器",
    "drqgd": "电容器鼓肚",
    "gcc_zc": "观察窗正常",
    "gcc_mh": "观察窗模糊",
    "gcc_ps": "观察窗破损",
    "ws_ywyc": "瓦斯观察窗油位下降",
    "bj_wkps": "表计外壳破损",
    "bj_bpmh": "表计表面模糊",
    "bj_bpps": "表计表盘破损",
    "bjdsyc_sx": "数显表计度数异常",
    "bjdsyc_zz": "指针表计度数异常",
    "bjdsyc_zz_hq": "表计读数异常指针红区",
    "bjzc": "表计正常",
    "bjdsyc_zz_cx": "表计读数异常指针超限",
    "bjdsyc_ywj": "油位计表计度数异常",
    "bjdsyc_ywc": "油位窗表计度数异常",
    "bjdszc_zz": "表计读数正常指针",
    "bjdszc_sx": "表计读数正常数显",
    "SF6ylb": "SF6表",
    "xldlb": "泄漏电流表",
    "hxq_gjtzc": "呼吸器硅胶桶正常",
    "ylb": "压力表",
    "ywb": "油温表",
    "ywj": "油位计",
    "ywc": "油位窗",
    "jyz_pl": "绝缘子破裂",
    "bmwh": "表面污秽",
    "yw_nc": "鸟巢",
    "wcgz": "未穿工装",
    "wcaqm": "未穿安全帽",
    "yw_gkxfw": "挂空悬浮物",
    "mbhp": "面板花屏",
    "xy": "吸烟",
    "yljdq_flow": "油漏继电器指示flow",
    "yljdq_stop": "油漏继电器指示stop",
    "kgg_ybf": "压板分",
    "kgg_ybh": "压板合",
    "kk_h": "空开合",
    "kk_f": "空开分",
    "xmbhyc": "箱门闭合异常",
    "xmbhzc": "箱门闭合正常",
    "zsd_l": "指示灯亮",
    "zsd_m": "指示灯灭",
    "qx_fhz_f": "球形分合闸分",
    "fhz_f": "分合闸分",
    "fhz_h": "分合闸合",
    "fhz_ztyc": "分合闸状态异常",
    "hzyw": "火灾烟雾",
    "yxdgsg": "引线断股松股",
    "jdyxxsd": "接地引下线松动",
    "jsxs_ddjt": "导电接头锈蚀",
    "jsxs_ddyx": "导电引线锈蚀",
    "jsxs_jdyxx": "接地引下线锈蚀",
    "jsxs_ecjxh": "二次接线盒锈蚀",
    "yx": "引线",
    "jdyxx": "接地引下线",
    "ecjxh": "二次接线盒",
    "ddjt": "导电接头",
    "fryc_blq": "避雷器发热异常",
    "fryc_tg": "套管发热异常",
    "fryc_dyhgq": "电压互感器发热异常",
    "fryc_dlhgq": "电流互感器发热异常",
    "fryc_ddjt": "引线接头发热异常",
    "qtjdq": "气体继电器",
    "zz_fhz_f": "指针分合闸分",
    "zz_fhz_h": "指针分合闸和",
    "zz_fhz_yc": "指针分合闸异常"
}

def read_txts(labels:list, path:str)->dict:
    """
    将生成的所有图片的检测结果按照标签类别进行分类(只取labels中的标签)，最终返回
    结果字典，{label:[id,name,type,xmin,ymin,xmax,ymax],..}
    Args:
        labels: 需要查看的类别标签
        path: 生成的单个的图片的检测结果文件路径
    Return:
        labels_dict: 所有生成的单个图片的检测结果txt文件信息。
    """
    if os.path.isfile(path): # 代码兼容输入为一个file而不是path
        path = os.path.dirname(path)
    labels_dict = dict()
    for label in labels:
        labels_dict[label] = list()
    if not os.path.exists(path):
        return labels_dict
    txts = os.listdir(path)
    txts_pth = [Path(path).joinpath(txt) for txt in txts]
    for txt_pth in txts_pth:
        with open(txt_pth, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line_list = line.strip().split(',')
                if line_list[2] in labels:
                    labels_dict[line_list[2]].append(line_list)
    # 检测结果按照confidence进行排序(逆序)
    for label, value in labels_dict.items():
        labels_dict[label] = sorted(value, key=lambda x: x[3], reverse=True)
    return labels_dict


def read_xmls(labels:list, path:str)->(dict,dict):
    """
    读取所有xml文件的object信息，并按照xml文件前缀名进行分类(只取labels中的标签)，最终返回
    结果字典，{'xmlname':{'label':{bbox:[..],'difficult':[..],'unsed':[..]}}
    Args:
        labels: 需要查看的类别标签
        path: xml文件路径
    Return:
        ndifficult: 所有标签中的difficult为0的总数，即所有类别的标注的总数
        objects_dict: 所有xml文件中标签的统计结果{'xmlname':{'label':{bbox:[..],'difficult':[..],'unsed':[..]}}
    """
    objects_dict = dict()
    if not os.path.exists(path):
        return objects_dict
    xmls = os.listdir(path)
    xmls_pth = [Path(path).joinpath(xml) for xml in xmls]
    # 按照标签对difficult=0进行数量统计
    ndifficult_dict = dict()
    for label in labels:
        ndifficult_dict[label] = 0
    # 遍历所有的xml文件，获取信息
    for index, xml_pth in enumerate(xmls_pth):
        with open(xml_pth, encoding='utf-8') as f:
            tree = ET.parse(f)
            # 获取当前xml文件的前缀名
            xmlname = os.path.splitext(xmls[index])[0]
            objects_dict[xmlname] = dict()
            # 初始化结果字典
            for label in labels:
                objects_dict[xmlname][label] = dict()
                objects_dict[xmlname][label]['bbox'] = list()
                objects_dict[xmlname][label]['difficult'] = list()
                objects_dict[xmlname][label]['used'] = list()
            # 获取所有xml文件中的object信息
            for obj in tree.findall('object'):
                name = obj.find('name').text
                # 标签合并
                if name in ["bjdsyc_zz_hq","bjdsyc_zz_cx"]:
                    name = "bjdsyc_zz"
                elif name in ["qx_fhz_f","zz_fhz_f"]:
                    name = "fhz_f"
                elif name in ["qx_fhz_h", "zz_fhz_h"]:
                    name = "fhz_h"
                elif name in ["qx_fhz_yc", "zz_fhz_yc"]:
                    name = "fhz_ztyc"
                elif name in ['zsd_l_qt']:
                    name = "zsd_l"
                elif name in ['zsd_m_qt']:
                    name = 'zsd_m'
                if name not in labels:
                    continue
                objects_dict[xmlname][name]['difficult'].append(0)
                bbox = obj.find('bndbox')
                objects_dict[xmlname][name]['bbox'].append([int(bbox.find('xmin').text),
                                                             int(bbox.find('ymin').text),
                                                             int(bbox.find('xmax').text),
                                                             int(bbox.find('ymax').text)])
                objects_dict[xmlname][name]['used'].append(False)
            # bbox和difficult从list转成numpy
            for label in labels:
                objects_dict[xmlname][label]['bbox'] = np.array(objects_dict[xmlname][label]['bbox']).astype(float)
                difficult = objects_dict[xmlname][label]['difficult']
                if difficult:
                    objects_dict[xmlname][label]['difficult'] = np.array(difficult).astype(bool)
                    ndifficult_dict[label] = ndifficult_dict[label] + sum(~objects_dict[xmlname][label]['difficult'])
    return ndifficult_dict, objects_dict    


def voc_ap(rec, prec, use_07_metric=False):
    """ ap = voc_ap(rec, prec, [use_07_metric])
    Compute VOC AP given precision and recall.
    If use_07_metric is true, uses the
    VOC 07 11 point method (default:False).
    根据rec，prec计算ap值，rec为x轴，prec为y轴
    Args:
        rec: 召回率的累加数组
        prec: 精确度的累加数组
    Return:
        ap: 当前类别的ap值
    """
    if use_07_metric:
        # 11 point metric
        ap = 0.
        for t in np.arange(0., 1.1, 0.1):
            if np.sum(rec >= t) == 0:
                p = 0
            else:
                p = np.max(prec[rec >= t])
            ap = ap + p / 11.
    else:
        # correct AP calculation
        # first append sentinel values at the end
        mrec = np.concatenate(([0.], rec, [1.]))
        mpre = np.concatenate(([0.], prec, [0.]))
        # compute the precision envelope
        # 确保曲线是单调的
        for i in range(mpre.size - 1, 0, -1):
            mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])
        # to calculate area under PR curve, look for points
        # where X axis (recall) changes value
        # 找到mrec中与相邻元素不同的位置，例如mrec=[0.,0.2,0.3,0.4,0.6,0.6,1.]
        # i = [0,1,2,3,4,6]，i为与相邻元素不同的下标位置，确保x轴是单调递增
        i = np.where(mrec[1:] != mrec[:-1])[0]
        # and sum (\Delta recall) * prec
        # 计算当前的pr曲线的面积，类似于先求单个面积：x[i+1]-x[i])*y[i+1]，再计算总和
        ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap


def calculate_ap(label, labels_dict, objects_dict, ndifficult_dict, ovthresh=0.5, time_scale=0.1):
    """
    计算召回率/精确度/AP值/总分(时间默认为满分)
    Args:
        label: 当前查看的类别标签
        labels_dict: txt文件中的检测信息
        objects_dict: xml文件中的标注信息
        ndifficult_dict: xml中所有标签的总数，按照标签类别分类
    Return:
        recalls[-1]: 当前类别的检测召回率
        precisions[-1]: 当前类别的检测精确度
        ap: 当前类别的检测ap值
        all_score: 当前类别的总分
    """
    if label not in labels_dict.keys():
        return 0.,0.,0.,0.
    results = labels_dict[label]
    # true_positive, 真正例
    tp = np.zeros(len(results))
    # false_positive, 假正例
    fp = np.zeros(len(results))
    for index, result in enumerate(results):
        name = os.path.splitext(result[1])[0]
        # txt文件中获取的bbox
        txt_bbox = np.array(result[-4:]).astype(float)
        # xml文件中获取的bboxes
        xml_bboxes = objects_dict[name][label]['bbox']
        if xml_bboxes.size > 0:
            # 计算txt文件中单个box和xml文件中同标签的所有box的iou，使用numpy并行计算
            ixmin = np.maximum(xml_bboxes[:, 0], txt_bbox[0])
            iymin = np.maximum(xml_bboxes[:, 1], txt_bbox[1])
            ixmax = np.minimum(xml_bboxes[:, 2], txt_bbox[2])
            iymax = np.minimum(xml_bboxes[:, 3], txt_bbox[3])
            iw = np.maximum(ixmax - ixmin + 1., 0.)
            ih = np.maximum(iymax - iymin + 1., 0.)
            inters = iw * ih
            # union
            unions = ((txt_bbox[2] - txt_bbox[0] + 1.) * 
                    (txt_bbox[3] - txt_bbox[1] + 1.) +
                    (xml_bboxes[:,2] - xml_bboxes[:,0] + 1.) * 
                    (xml_bboxes[:,3] - xml_bboxes[:,1] + 1.) - inters)
            ious = inters / unions
            ioumax = np.max(ious)
            jmax = np.argmax(ious)
            # 个别类别的iou阈值需要单独处理
            if label in ['sly_bjbmyw','sly_dmyw', 'yw_gkxfw']:
                ovthresh = 0.3
            if ioumax >= ovthresh:
                if not objects_dict[name][label]['difficult'][jmax]:
                    if not objects_dict[name][label]['used'][jmax]:
                        tp[index] = 1.
                        objects_dict[name][label]['used'][jmax] = True
                    else: # 同一个标签检测出了多个同类别的框，属于错检
                        fp[index] = 1.
            else: # iou 低于当前设置的阈值，属于错检
                fp[index] = 1.
        else: # xml文件中不存在当前类别，属于多检
            fp[index] = 1.

    # 获取fp和tp的累加数组
    fp_sum = np.cumsum(fp)
    tp_sum = np.cumsum(tp)
    # 计算召回率/精确度/ap
    recalls = tp_sum / float(ndifficult_dict[label])
    # 避免除0
    precisions = tp_sum / np.maximum(tp_sum + fp_sum, np.finfo(np.float64).eps)
    ap = voc_ap(recalls, precisions)
    if len(recalls):
        # 计算总分
        all_score = 100*(ap*0.3 + recalls[-1]*0.3 + precisions[-1]*0.3 + time_scale)
        return recalls[-1], precisions[-1], ap, all_score
    else:
        return 0.,0.,0.,0.
    

def output_result(labels, results, ndifficult_dict, result_name):
    """
    输出召回率/精确度/AP值/总分(时间默认为满分)，并生成result.csv结果文件
    Args:
        label: 当前查看的类别标签
        results: 当前类别的rec,prec,ap,all_score
        ndifficult_dict: xml中所有标签的总数，按照标签类别分类
        result_name: 保存的结果文件
    Return:
        None
    """
    f = open(result_name,'w',encoding='utf-8-sig')
    headers = ['类别','验证集数','检出','误检','ap','总分']
    writer = csv.writer(f)
    writer.writerow(headers)
    for i, label in enumerate(labels):
        print('---------------------')
        print("iou:{:.2f} type:{:<10} \t检出率 = {:.4f}, \t误检率 = {:.4f}, \tAP值 = {:.4f}, \t总分 = {:.4f}"
        .format(0.5, label, results[i][0]*100, (1-results[i][1])*100, results[i][2], results[i][3]))
        cname = detect_dict[label]
        num = ndifficult_dict[label]
        writer.writerow([cname, 
                         num, 
                         "{:.2f}".format(results[i][0]*100), 
                         "{:.2f}".format((1-results[i][1])*100), 
                         "{:.4f}".format(results[i][2]), 
                         "{:.4f}".format(results[i][3])])


def eval_batch(xmls_pth, txt_pth, labels, resultcsv):
    ovthresh = 0.5
    labels_dict = read_txts(labels, txt_pth)
    ndifficult_dict, objects_dict = read_xmls(labels, xmls_pth)
    results = list()
    # 遍历标签
    for label in labels:
        # 计算单个类别的recall，preciosn，ap，总分
        recall, precision, ap, all_score = calculate_ap(label, labels_dict, objects_dict, ndifficult_dict)
        results.append([recall, precision, ap, all_score])
    # 打印和输出result.csv结果文件
    output_result(labels, results, ndifficult_dict, resultcsv)


if __name__ == '__main__':
    imgs_pth = '/jlk/data/sb_data_beijing/rename/images/'  # 检测图像路径
    xmls_pth = '/jlk/data/sb_data_beijing/rename/xmls/'  # 标签文件存放路径
    txt_pth = '/usr/src/sb_model/txts/result.txt'  # 检测生成的txt路径
    labels = ['sly_bjbmyw', 'cysb_cyg', 'cysb_sgz', 'cysb_tg', 'cysb_lqq', 'cysb_qyb', 'cysb_qtjdq', 'ylsff', 
              'sly_dmyw', 
              'pzqcd', 
              'jyhbx', 
              'drqgd', 
              'jyz_pl', 
              'yxdgsg', 'yx',
              'jdyxxsd', 'jdyxx', 
              'ws_ywyc', 
              'fhz_f', 'fhz_h', 'fhz_ztyc', 
              'bj_wkps', 'bj_bpps', 'bj_bpmh', 'ywj', 'SF6ylb', 'xldlb', 'ywb', 'ywc', 
              'bjdsyc_zz',
              'bjdsyc_ywj', 
              'bjdsyc_ywc']
    eval_batch(xmls_pth, txt_pth, labels, "result.csv")
