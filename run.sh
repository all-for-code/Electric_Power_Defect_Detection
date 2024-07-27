#!/bin/bash
#author: lijiang🚀
#data: 2023-12-20🚀

python run.py --imgpth '/jlk/data/sb_data_beijing/rename/images/file.txt' \
              --bs 8 \
              --imgsz 1024 \
              --wpth 'model/1229_48_1024_l_240b_200e/weights/best.pt' \
              --nw 8 \
              --cid 3 \
              --stateurl 'http://localhost:8080/pcr/contest/submit_state' \
              --resulturl 'http://localhost:8080/pcr/contest/submit_result' \
              --stfile '/usr/src/sb_model/txts/result.txt' \
              --verbose
            #   --stfile '/usr/src/sb_model/txts/result.txt'
            #   --xmlpth '/jlk/data/sb_data_beijing/rename/xmls'
	        #   --saveimgpth '/usr/src/sb_model/images/'