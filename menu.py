import nuke
import zay_tp_manager


bar = nuke.menu('Nodes')
toolbar = bar.addMenu("Z")
toolbar.addCommand('pipline/ZayTPManager', zay_tp_manager.run_show_funa)
