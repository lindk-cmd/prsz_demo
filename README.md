# prsz_demo
1. 安装环境
安装python环境以及pytorch
python版本要求3.7以上

以anaconda为例安装：
conda create -n yolox_dect python=3.7 -y
conda activate yolox_dect
conda install pytorch==1.7.0 torchvision==0.8.0 torchaudio==0.7.0 cudatoolkit=10.2 -c pytorch -y

编译项目进行本地安装：
cd prsz_python_demo
pip3 install -U pip && pip3 install -r requirements.txt
pip3 install -v -e .

安装BboxToolkit：
cd BboxToolkit
python setup.py develop


2. demo运行
python tools/demo.py -expn prsz_loaction_det -c YOLOX_outputs/prsz_loaction_det/best_ckpt.pth -f exps/example/prsz_det/prsz_location_det.py --path ./IMG_8178.JPG --fuse  --device cpu --save_result --output_format obb

参数说明:
-expn: 实验名称
-c: 模型文件保存路径
-f: 实验配置文件
--path: 待预测图片路径
--device:设置cpu或GPU推理
--save_result：是否保存结果

