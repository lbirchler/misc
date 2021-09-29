from source import get_source
from stix2 import TAXIICollectionSource, Filter
from taxii2client.v20 import Collection
from datetime import datetime
import pandas as pd
import textwrap


def wrap_text(label, txt):
    my_wrap = textwrap.TextWrapper(width=60)
    wrap_list = my_wrap.wrap(text=txt)
    count = 1
    for line in wrap_list:
        if count <= 1:
            print(f"{label}\t{line}".expandtabs(25))
            count += 1
        else:
            print(f"\t{line}".expandtabs(25))
    return


def regular_text(label, txt):
    print(f"{label}:\t{txt}".expandtabs(25))
    return


def print_text(data):
    for x in data:
        if x["tactic"] is not None:
            try:
                regular_text("mitre_id", x["mitre_id"])
                regular_text("tactic", x["tactic"])
                regular_text("technique", x["technique"])
                regular_text("technique_name", x["technique_name"])
                regular_text("created", x["created"])
                regular_text("modified", x["modified"])
                wrap_text("technique_desc:", x["technique_desc"])
                regular_text("permissions_required", x["permissions_required"])
                regular_text("platforms", x["platforms"])
                wrap_text("data_sources", x["data_sources"])
                regular_text("stix_id", x["stix_id"])
                print("\n---\n")
            except AttributeError as e:
                print("Error: {e}")
    return


def get_techniques(thesrc):
    techniques = thesrc.query([Filter("type", "=", "attack-pattern")])

    def extract_technique_data(teq, fld):
        if fld == "tactic":
            try:
                for j in range(len(teq[i]["kill_chain_phases"])):
                    return teq[i]["kill_chain_phases"][j]["phase_name"]
            except KeyError:
                return None
        elif fld == "external_references":
            try:
                for j in range(len(teq[i]["external_references"])):
                    return teq[i]["external_references"][j]["external_id"]
            except KeyError:
                return None
        elif fld in ["created", "modified"]:
            try:
                return datetime.date(teq[i][fld])
            except KeyError:
                return None
        elif fld in [
            "x_mitre_permissions_required",
            "x_mitre_platforms",
            "x_mitre_data_sources",
        ]:
            try:
                return ", ".join(teq[i][fld])
            except KeyError:
                return None
        else:
            try:
                return teq[i][fld]
            except KeyError:
                return None

    technique_d = []
    for i in range(len(techniques)):
        d = {
            "mitre_id": extract_technique_data(techniques, "external_references"),
            "tactic": extract_technique_data(techniques, "tactic"),
            "technique_name": extract_technique_data(techniques, "name"),
            "technique_desc": extract_technique_data(techniques, "description"),
            "permissions_required": extract_technique_data(
                techniques, "x_mitre_permissions_required"
            ),
            "platforms": extract_technique_data(techniques, "x_mitre_platforms"),
            "data_sources": extract_technique_data(techniques, "x_mitre_data_sources"),
            "created": extract_technique_data(techniques, "created"),
            "modified": extract_technique_data(techniques, "modified"),
            "stix_source_type": extract_technique_data(techniques, "type"),
            "stix_id": extract_technique_data(techniques, "id"),
        }
        technique_d.append(d)
    # add technique key, value
    for t in technique_d:
        t["technique"] = t["mitre_id"][0:5]

    return [pd.DataFrame(technique_d), technique_d]


def main():
    src = get_source()
    mitre_techniques = get_techniques(thesrc=src)
    print_text(mitre_techniques[1])


if __name__ == "__main__":
    main()
