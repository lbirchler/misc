from source import get_source
from stix2 import TAXIICollectionSource, Filter
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
        try:
            regular_text("mitre_id", x["mitre_id"])
            regular_text("group_name", x["group_name"])
            regular_text("group_aliases", x["group_aliases"])
            regular_text("created", x["created"])
            regular_text("modified", x["modified"])
            wrap_text("group_desc:", x["group_desc"])
            regular_text("stix_id", x["stix_id"])
            print("\n---\n")
        except AttributeError as e:
            print("Error: {e}")
    return


def get_groups(thesrc):
    """gather all Mitre ATT&CK Groups"""
    groups = thesrc.query(
        [
            Filter("type", "=", "intrusion-set"),
            Filter("external_references.source_name", "=", "mitre-attack"),
            Filter("external_references.external_id", "contains", "G"),
        ]
    )

    def extract_group_data(grp, fld):
        if fld == "aliases":
            try:
                return ", ".join(grp[i]["aliases"])
            except KeyError:
                return None
        elif fld == "external_references":  # mitre group id
            try:
                for j in range(len(grp[i]["external_references"])):
                    return grp[i]["external_references"][j]["external_id"]
            except KeyError:
                return None
        elif fld in ["created", "modified"]:
            try:
                return datetime.date(grp[i][fld])
            except KeyError:
                return None
        else:
            try:
                return grp[i][fld]
            except KeyError:
                return None

    group_d = []
    for i in range(len(groups)):
        d = {
            "mitre_id": extract_group_data(groups, "external_references"),
            "group_name": extract_group_data(groups, "name"),
            "group_aliases": extract_group_data(groups, "aliases"),
            "group_desc": extract_group_data(groups, "description"),
            "created": extract_group_data(groups, "created"),
            "modified": extract_group_data(groups, "modified"),
            "stix_source_type": extract_group_data(groups, "type"),
            "stix_id": extract_group_data(groups, "id"),
        }
        group_d.append(d)

    return [pd.DataFrame(group_d), group_d]


def main():
    src = get_source()
    mitre_groups = get_groups(thesrc=src)
    print_text(mitre_groups[1])


if __name__ == "__main__":
    main()
