#coding=utf-8
#author: lijiang🚀
#data: 2023-12-20🚀

allcls = ['sly_bjbmyw', 'cysb_cyg', 'cysb_sgz', 'cysb_tg', 'cysb_lqq', 'cysb_qyb', 'cysb_qtjdq', 'ylsff', 
          'sly_dmyw', 
          'pzqcd', 
          'jyhbx', 
          'drqgd', 
          'jyz_pl', 
          'yxdgsg', 'yx',
          'jdyxxsd', 'jdyxx', 
          'ws_ywyc', 
          'zz_fhz_f', 'zz_fhz_h', 'zz_fhz_yc', 
          'qx_fhz_f', 'qx_fhz_h', 'qx_fhz_yc', 
          'bj_wkps', 'bj_bpps', 'bj_bpmh', 'ywj', 'SF6ylb', 'xldlb', 'ywb', 'ywc', 
          'bjdsyc_zz_hq', 'bjdsyc_zz_cx', 
          'bjdsyc_ywj', 
          'bjdsyc_ywc'] #36 beijing

outputcls = ['sly_bjbmyw', 'cysb_cyg', 'cysb_sgz', 'cysb_tg', 'cysb_lqq', 'cysb_qyb', 'cysb_qtjdq', 'ylsff', 
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

conf = {'sly_bjbmyw': 0.15, 'cysb_cyg': 0.25, 'cysb_sgz': 0.25, 'cysb_tg': 0.25, 'cysb_lqq': 0.25, 'cysb_qyb': 0.25, 'cysb_qtjdq': 0.25, 'ylsff': 0.25, 
        'sly_dmyw': 0.15, 
        'pzqcd': 0.15, 
        'jyhbx': 0.25, 
        'drqgd': 0.25, 
        'jyz_pl': 0.25, 
        'yxdgsg': 0.15, 'yx': 0.25,
        'jdyxxsd': 0.25, 'jdyxx': 0.25, 
        'ws_ywyc': 0.25, 
        'zz_fhz_f': 0.15, 'zz_fhz_h': 0.15, 'zz_fhz_yc': 0.15, 
        'qx_fhz_f': 0.15, 'qx_fhz_h': 0.15, 'qx_fhz_yc': 0.15, 
        'bj_wkps': 0.15, 'bj_bpps': 0.15, 'bj_bpmh': 0.15, 'ywj': 0.25, 'SF6ylb': 0.25, 'xldlb': 0.25, 'ywb': 0.25, 'ywc': 0.25, 
        'bjdsyc_zz_hq': 0.15, 'bjdsyc_zz_cx': 0.15, 
        'bjdsyc_ywj': 0.15, 
        'bjdsyc_ywc': 0.15}

# 过滤规则字典，key为缺陷标签，values为缺陷标签所在的部件标签
bindingcls = {'sly_bjbmyw': ['cysb_cyg', 'cysb_sgz', 'cysb_tg', 'cysb_lqq', 'cysb_qyb', 'cysb_qtjdq', 'ylsff'],
              'pzqcd': ['pzq'],
              'jyhbx': ['jyh'],
              'drqgd': ['drq'],
              'yxdgsg': ['yx'],
              'jdyxxsd': ['jdyxx'],
              'ws_ywyc': ['cysb_qtjdq'],
              'bj_wkps': ['ywj', 'SF6ylb', 'xldlb', 'ywb', 'ywc', 'cysb_qtjdq'],
              'bj_bpps': ['ywj', 'SF6ylb', 'xldlb', 'ywb', 'ywc', 'cysb_qtjdq'],
              'bj_bpmh': ['ywj', 'SF6ylb', 'xldlb', 'ywb', 'ywc', 'cysb_qtjdq'],
              'bjdsyc_zz_hq': ['SF6ylb', 'xldlb', 'ywb'],
              'bjdsyc_zz_cx': ['SF6ylb', 'xldlb', 'ywb'],
              'bjdsyc_ywj': ['ywj'],
              'bjdsyc_ywc': ['ywc']}
             
# 未标注的部件标签
ununitcls = ['pzq', 'jyh', 'drq']

unitcls = ['cysb_cyg', 'cysb_sgz', 'cysb_tg', 'cysb_lqq', 'cysb_qyb', 'cysb_qtjdq', 'ylsff',
           'pzq',
           'jyh',
           'drq',
           'yx',
           'jdyxx',
           'ywj', 'SF6ylb', 'xldlb', 'ywb', 'ywc']

filtercls = ['sly_bjbmyw', 'sly_dmyw']

# 判断缺陷和部件是否同时存在的iou阈值, sly_bjbmyw和yxdgsg的缺陷和部件比较特殊，iou设置最小
bindingiou = {'sly_bjbmyw': 0.01,
             'pzqcd': 0.1,
             'jyhbx': 0.1,
             'drqgd': 0.1,
             'yxdgsg': 0.001,
             'jdyxxsd': 0.1,
             'ws_ywyc': 0.1,
             'bj_wkps': 0.1,
             'bj_bpps': 0.1,
             'bj_bpmh': 0.1,
             'bjdsyc_zz_hq': 0.1,
             'bjdsyc_zz_cx': 0.1,
             'bjdsyc_ywj': 0.1,
             'bjdsyc_ywc': 0.1} # 部件标签

# 用于合并标签
mergecls = {"bjdsyc_zz_hq":"bjdsyc_zz", "bjdsyc_zz_cx":"bjdsyc_zz",
            "qx_fhz_f":"fhz_f", "zz_fhz_f":"fhz_f",
            "qx_fhz_h":"fhz_h", "zz_fhz_h":"fhz_h",
            "qx_fhz_yc":"fhz_ztyc", "zz_fhz_yc":"fhz_ztyc",
            'zsd_l_qt':"zsd_l",
            'zsd_m_qt':'zsd_m'}
