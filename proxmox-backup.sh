#!/bin/bash -e

# BACKUP PROXMOX VM

# before running make sure backup storage is enabled in web ui 
# - go to Datacenter > Storage.
# - select the backup storage location.
# - click on edit tab.
# - make sure to select backups/VZDump backup file under content
# - click ok

usage()
{
echo "Backup Proxmox VM"
echo
echo "Usage: $0 -v VMID -s SSH"
echo
echo "Options:"
echo "    -v VMID vmid of vm to backup"
echo "    -s SSH copy vm to remote server"
echo 
echo "Examples:"
echo "    - local:  root@pve:~# ./proxmox-backup -v 100"
echo "    - remote: root@pve:~# ./proxmox-backup -v 100 -s user@remote:/backups"
}

backup_vm()
{
    echo "[+] stopping vm"
    qm stop $1

    echo "[+] backing up vm"
    cd /var/lib/vz/dump
    vzdump $1 | tee /tmp/out # needed to grep for backup file path
}

get_backup_file_path()
{
    grep "creating vzdump archive" /tmp/out | grep -Po "'.*?'" | sed "s/'//g"
    rm /tmp/out
}

remote_save()
{
    BACKUP_FILE="$(get_backup_file_path)"

    echo "[+] copying backup to remote server"
    rsync -avP -e ssh $BACKUP_FILE $1

    echo "[+] deleting local backup"
    rm $BACKUP_FILE
}

VMID=
SSH=
while getopts ":v:s:h" opt; do
    case $opt in
        h)
            usage
            exit
            ;;
        v)
            VMID="$OPTARG"
            ;;
        s)
            SSH="$OPTARG"
            ;;
        \?)        
            usage
            exit
            ;;
    esac
done

# backup only
if [ -n "$VMID" ] && [ -z "$SSH" ]; then
    backup_vm $VMID
fi

# backup and copy to remote
if [ -n "$SSH" ]; then 
    if [ -z "$VMID" ]; then
        echo "[!] must specify vmid"
        usage
        exit 1
    fi
    backup_vm $VMID
    remote_save $SSH
fi

# usage
if [ -z "$VMID" ] && [ -z "$SSH" ]; then
    usage
    exit
fi
