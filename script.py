# call ubcalend_text.py and ubcexplorerscript.py
## Assume everything is done
# assume you have final_course which is an array

from ubcexplorerscript import UBCExplorerScript

def main(event, context):
    ubcexplorerscriptobj = UBCExplorerScript()
    data = ubcexplorerscriptobj.main()
    return data

main(None, None)