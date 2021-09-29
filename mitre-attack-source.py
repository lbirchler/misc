from stix2 import TAXIICollectionSource, Filter
from taxii2client.v20 import Collection


def get_source(matrix="enterprise_attack"):
    """access attack data from TAXII Server"""
    collections = {
        "enterprise_attack": "95ecc380-afe9-11e4-9b6c-751b66dd541e",
        "mobile_attack": "2f669986-b40b-4423-b720-4396ca6a462b",
        "ics-attack": "02c3ef24-9cd4-48f3-a99f-b74ce24f1d34",
    }
    try:
        collection = Collection(
            f"https://cti-taxii.mitre.org/stix/collections/{collections[matrix]}/"
        )
        src = TAXIICollectionSource(collection)
        return src
    except:
        print(
            "Matrix not collected:\nSelect one of the following; enterprise_attack, mobile_attack, ics_attack"
        )
