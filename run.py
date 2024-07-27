#coding=utf-8
#author: lijiang🚀
#data: 2023-12-20🚀

import argparse
from recognize.inference import Inference
import time
from pathlib import Path
import os

def parse_args() -> argparse.Namespace:
    parse = argparse.ArgumentParser()
    group_txt = parse.add_mutually_exclusive_group()
    server = parse.add_argument_group()
    parse.add_argument(
        "--imgsz",
        "--image_size",
        type=int,
        default=1024,
        required=False,
        help="A batch image size for onnx or tensorrt inference, just only one number. Defaults to 1024",
    )
    parse.add_argument(
        "--bs",
        "--batch_size",
        type=int,
        default=8,
        required=False,
        help="The number of images used in one inference, which should be consistent with tensorrt's batchsize. Defaults to 8",
    )
    parse.add_argument(
        "--imgpth",
        "--image_path",
        type=str,
        default=None,
        required=True,
        help="Image path for onnx or tensorrt inference, which is not allowed to be empty. Defaults to None",
    )
    parse.add_argument(
        "--wpth",
        "--weight_path",
        type=str,
        default=None,
        required=True,
        help="Weight file path for onnx or tensorrt inference, which is not allowed to be empty. Defaults to None",
    )
    parse.add_argument(
        "--xmlpth",
        "--xml_path",
        type=str,
        default=None,
        required=False,
        help="The path to the xml file of all the images used to calculate pr. Defaults to None",
    )  
    parse.add_argument(
        "--nw",
        "--num_workers",
        type=int,
        default=8,
        required=False,
        help="Number of the processes that load images. Defaults to None",
    )
    parse.add_argument(
        "--saveimgpth",
        "--save_image_path",
        type=str,
        default=None,
        required=False,
        help="The path to save the image with the boxes drawn. Defaults to None",
    )
    parse.add_argument(
        "--resultcsv",
        "--result_csv",
        type=str,
        default='result.csv',
        required=False,
        help="The path to save the csv file of detection. Defaults to None",
    )
    parse.add_argument(
        "--verbose",
        "--verbose_yolo",
        action="store_true",
        help="Whether to output YOLO's print information. Defaults to None",
    )
    group_txt.add_argument(
        "--stpth",
        "--save_txt_path",
        type=str,
        default=None,
        required=False,
        help="The path to save the txt files, which is mutually exculsive with --save_txt_file;\
              In this mode, the txt file name is the same as the image name and the number of txt files is equal to number of images;\
              Defaults to None"
    )
    group_txt.add_argument(
        "--stfile",
        "--save_txt_file",
        type=str,
        default=None,
        required=False,
        help="The path to save the txt file, which is mutually exculsive with --save_txt_path;\
              In this mode, only a txt file is generated, which contains the detection results of all images\
              and can't use the --xmlpth to calculate the pr;\
              Defaults to None",
    )
    server.add_argument(
        "--stateurl",
        "--state_url",
        type=str,
        default=None,
        required=False,
        help="Ip address of the server that receives the heartbeat. Defaults to None; \
              this parameter needs to be used with --result_url together",
    )
    server.add_argument(
        "--resulturl",
        "--result_url",
        type=str,
        default=None,
        required=False,
        help="Ip address of the server that receives the detect result. Default to None; \
              this parameter needs to be used with --state_url together",
    ) 
    server.add_argument(
        "--cid",
        "--contestant_id",
        type=int,
        default=None,
        required=False,
        help="Id number of the manufacturer. Default to None",
    ) 
    return parse.parse_args()

def run():
    time0 = time.time()
    args = parse_args()
    urls = [vars(args)['resulturl'], vars(args)['stateurl']]
    url_num = len([url for url in urls if url != None])
    if url_num in range(1,2):
        raise RuntimeError("--stateurl and --resulturl should be used together")
    inference = Inference(**vars(args))
    inference()
    time1 = time.time()
    if os.path.isdir(vars(args)['imgpth']):
        print(f"avg one pic cost time: {(time1-time0)/(len(os.listdir(vars(args)['imgpth'])))*1000}ms")
    else:
        folder = os.path.dirname(vars(args)['imgpth'])
        print(f"avg one pic cost time: {(time1-time0)/(len(os.listdir(folder)) - 1)*1000}ms")

if __name__ == "__main__":
    run()
