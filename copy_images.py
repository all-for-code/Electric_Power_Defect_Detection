import os,shutil

imgpth = 'testimages/images'

imgs = os.listdir(imgpth)

times = 2
for i in range(times):
    for img in imgs:
        shutil.copy(os.path.join(imgpth, img), os.path.join(imgpth, img[0:-4] + f"{i}.jpg"))
        shutil.copy(os.path.join(os.path.dirname(imgpth),"xmls",img[0:-4]+".xml"), os.path.join(os.path.dirname(imgpth),"xmls", img[0:-4] + f"{i}.xml"))

