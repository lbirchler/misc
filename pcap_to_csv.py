from scapy.all import *
import pandas as pd
import binascii
import argparse
import sys

def pcap_to_df(pcap):
    ip_fields = [field.name for field in IP().fields_desc]
    tcp_fields = [field.name for field in TCP().fields_desc]
    udp_fields = [field.name for field in UDP().fields_desc]
    dataframe_fields = ip_fields + ['time'] + tcp_fields + ['payload','payload_raw','payload_hex']

    df = pd.DataFrame(columns=dataframe_fields)

    for packet in pcap[IP]:
        field_values = []
        for field in ip_fields:
            if field == 'options':
                field_values.append(len(packet[IP].fields[field]))
            else:
                field_values.append(packet[IP].fields[field])
        field_values.append(packet.time)
        layer_type = type(packet[IP].payload)

        for field in tcp_fields:
            try:
                if field == 'options':
                    field_values.append(len(packet[layer_type].fields[field]))
                else:
                    field_values.append(packet[layer_type].fields[field])
            except:
                field_values.append(None)

        field_values.append(len(packet[layer_type].payload))
        field_values.append(packet[layer_type].payload.original)
        field_values.append(binascii.hexlify(packet[layer_type].payload.original))

        df_append = pd.DataFrame([field_values], columns=dataframe_fields)
        df = pd.concat([df, df_append], axis=0)

    df.reset_index(inplace=True)
    df.drop(columns="index", inplace=True)

    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", type=str, help="input pcap file")
    parser.add_argument("-o", "--output_file", type=str, help="output csv file")
    args = parser.parse_args()

    try:
        pcap = rdpcap(args.input_file)
    except:
        print(f"error importing pcap file")
        sys.exit(1)

    try:
        df = pcap_to_df(pcap)
    except:
        print("error with: pcap_to_df()")
        sys.exit(1)

    try:
        df.to_csv(args.output_file, index=None)
        print(f"exported pcap df to: {args.output_file}")
    except:
        print("error exporting pcap csv file")
        sys.exit(1)

if __name__ == "__main__":
    main()
