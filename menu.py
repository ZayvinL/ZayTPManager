import nuke
import tppanel




bar = nuke.menu('Nodes')
toolbar = bar.addMenu("Z")
toolbar.addCommand('pipline/tempplate_Panel', tppanel.run_show_funa)







