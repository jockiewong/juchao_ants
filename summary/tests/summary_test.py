import os
import sys

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, "../.."))
sys.path.insert(0, file_path)


from summary.final_sf_const_announcement import FinalConstAnn
from summary.final_sf_secu_announcement_detail import FinalAntDetail
from summary.final_sf_secu_announcement_summary import FinalAntSummary

# final_const = FinalConstAnn()
# final_const.launch()


final_detail = FinalAntDetail()
final_detail.daily_update()


# final_summary = FinalAntSummary()
# final_summary.daily_update()
