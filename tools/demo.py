#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) Megvii, Inc. and its affiliates.

import argparse
import os
import time
from loguru import logger

import torch

# from yolox.data.data_augment import ValTransform
from yolox.exp import get_exp
from yolox.utils import (fuse_model, get_model_info, postprocess, 
                         DictAction, Predictor, image_demo, imageflow_demo)



def make_parser():
    parser = argparse.ArgumentParser("智能检测 Demo!")
    parser.add_argument("-expn", "--experiment-name", type=str, default=None)
    parser.add_argument("-n", "--name", type=str, default=None, help="model name")

    parser.add_argument(
        "--path", default="./assets/dog.jpg", help="path to images"
    )
    parser.add_argument("--camid", type=int, default=0, help="webcam demo camera id")
    parser.add_argument(
        "--save_result",
        action="store_true",
        help="whether to save the inference result of image/video",
    )
    parser.add_argument(
        "--output_format", 
        nargs="+", choices=["bbox", "mask", "obb"],
        default="obb")
    # exp file
    parser.add_argument(
        "-f",
        "--exp_file",
        default=None,
        type=str,
        help="pls input your experiment description file",
    )
    parser.add_argument("-c", "--ckpt", default=None, type=str, help="ckpt for eval")
    parser.add_argument(
        "--device",
        default="cpu",
        type=str,
        help="device to run our model, can either be cpu or gpu",
    )
    parser.add_argument(
        "--fp16",
        dest="fp16",
        default=False,
        action="store_true",
        help="Adopting mix precision evaluating.",
    )
    parser.add_argument(
        "--legacy",
        dest="legacy",
        default=False,
        action="store_true",
        help="To be compatible with older versions",
    )
    parser.add_argument(
        "--fuse",
        dest="fuse",
        default=False,
        action="store_true",
        help="Fuse conv and bn for testing.",
    )
    parser.add_argument(
        "--options",
        nargs="+",
        action=DictAction,
        help="setting some uncertainty values"
    )
    return parser

def main(exp, args):
    if not args.experiment_name:
        args.experiment_name = exp.exp_name
    else:
        exp.exp_name = args.experiment_name

    if len(args.output_format) == 1:
        args.output_format = args.output_format[0]

    file_name = os.path.join(exp.output_dir, args.experiment_name)
    os.makedirs(file_name, exist_ok=True)

    vis_folder = None
    if args.save_result:
        vis_folder = os.path.join(file_name, "vis_res")
        os.makedirs(vis_folder, exist_ok=True)

    logger.info("Args: {}".format(args))
    logger.info("Merge Info of the Args")
    exp.merge(args.options)
    model = exp.get_model()
    logger.info("Model Summary: {}".format(get_model_info(model, exp.test_size)))

    device = torch.device(args.device)
    model.to(device)
    if device.type == "cuda" and args.fp16:
        model.half()  # to FP16
    model.eval()

    if args.ckpt is None:
        ckpt_file = os.path.join(file_name, "best_ckpt.pth")
    else:
        ckpt_file = args.ckpt

    # 模型读取
    logger.info("loading checkpoint")
    # ckpt = torch.load(ckpt_file, map_location="cpu")
    ckpt = torch.load(ckpt_file, map_location=device)
    # load the model state dict
    model.load_state_dict(ckpt["model"], strict=True)
    logger.info("loaded checkpoint done.")
    if args.fuse:
        logger.info("\tFusing model...")
        model = fuse_model(model)

    # 预测前进行初始化
    predictor = Predictor(
        model, 
        exp, 
        None,
        None,
        getattr(model, "postprocess", postprocess),
        args.device, 
        args.fp16, 
        args.legacy,
        output_format=args.output_format)
    current_time = time.localtime()

    image_demo(predictor, vis_folder, args.path, current_time, args.save_result)


if __name__ == "__main__":
    args = make_parser().parse_args()
    exp = get_exp(args.exp_file, args.name)
    print(exp)
    main(exp, args)
