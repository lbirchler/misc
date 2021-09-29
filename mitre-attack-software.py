from source import get_source
import pandas as pd
from itertools import chain
from stix2 import Filter
from datetime import datetime
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
            regular_text("software_name", x["software_name"])
            regular_text("created", x["created"])
            regular_text("modified", x["modified"])
            wrap_text("software_desc", x["software_desc"])
            regular_text("stix_id", x["stix_id"])
            print("\n---\n")
        except AttributeError as e:
            print("Error: {e}")
    return


def get_software(thesrc):
    software = list(
        chain.from_iterable(
            thesrc.query(f)
            for f in [Filter("type", "=", "tool"), Filter("type", "=", "malware")]
        )
    )

    def extract_software_data(sft, fld):
        if fld == "external_references":
            try:
                for j in sft:
                    return j["external_references"][0]["external_id"]
            except KeyError:
                return None
        elif fld in ["created", "modified"]:
            try:
                return datetime.date(sft[i][fld])
            except KeyError:
                return None
        else:
            try:
                return sft[i][fld]
            except KeyError:
                return None

    software_d = []
    for i in range(len(software)):
        d = {
            "mitre_id": extract_software_data(software, "external_references"),
            "software_name": extract_software_data(software, "name"),
            "software_desc": extract_software_data(software, "description"),
            "created": extract_software_data(software, "created"),
            "modified": extract_software_data(software, "modified"),
            "stix_source_type": extract_software_data(software, "type"),
            "stix_id": extract_software_data(software, "id"),
        }
        software_d.append(d)

    return [pd.DataFrame(software_d), software_d]


def main():
    src = get_source()
    mitre_software = get_software(thesrc=src)
    print_text(mitre_software[1])


if __name__ == "__main__":
    main()
