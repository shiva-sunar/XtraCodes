######################################################## Clone and Restore DD Image , using DD and Clonezill






################ Code to Clone a DD image of the Windows OS/Disk
# List all block devices
lsblk

# Mount the second partition of /dev/sdb to /mnt
mount /dev/sdb2 /mnt

# Copy the contents of /dev/sda to /mnt/clipped.dd in 256 MB chunks, showing progress
dd if=/dev/sda of=/mnt/clipped.dd bs=256M count=60000000000 iflag=count_bytes status=progress







################ Code to Restore a DD image of the Windows OS/Disk
# List all block devices
lsblk

# Delete partition table of /dev/sda
sfdisk --delete /dev/sda

# Mount /dev/sdb2 to /mnt
mount /dev/sdb2 /mnt

# Copy the contents of /mnt/clipped.dd to /dev/sda with a block size of 256M and show progress
dd if=/mnt/clipped.dd of=/dev/sda bs=256M status=progress

# Erase/Correct the partition table of /dev/sda
sgdisk -e /dev/sda

# Resize partition 3 of /dev/sda to 235GiB
parted /dev/sda resizepart 3 235GiB

# Resize the NTFS file system on /dev/sda3
ntfsresize --force --force /dev/sda3





# New Menuentry to be added in grub.cfg of clonezilla.
menuentry "Start Shell" --id live-shell {
  search --set -f /live/vmlinuz
  $linux_cmd /live/vmlinuz boot=live union=overlay username=user config components quiet loglevel=0 noswap edd=on nomodeset enforcing=0 locales=en_US.UTF-8 keyboard-layouts=us ocs_live_run="sudo bash" ocs_live_extra_param="" ocs_live_batch="no" vga=788 ip= net.ifnames=0  nosplash i915.blacklist=yes radeonhd.blacklist=yes nouveau.blacklist=yes vmwgfx.enable_fbdev=1
  $initrd_cmd /live/initrd.img
}


menuentry "Inbound FR SATA" --id live-ios {
  search --set -f /live/vmlinuz
  $linux_cmd /live/vmlinuz boot=live union=overlay username=user config components quiet loglevel=0 noswap edd=on nomodeset enforcing=0 locales=en_US.UTF-8 keyboard-layouts=us ocs_live_run="echo 'Displaying the Disks'; echo '#############################################'; lsblk; echo 'Mounting the Images drive to /mnt'; echo '#############################################'; mount /dev/sdb2 /mnt; echo 'Formatting/Deleting the Interal Drive'; echo '#############################################'; sfdisk --delete /dev/sda; echo 'Copying the DD File to Internal Disk'; echo '#############################################'; dd if=/mnt/in.fr.20231228.dd of=/dev/sda bs=256M status=progress; echo 'Fixing the Backup Partiion Table'; echo '#############################################'; sgdisk -e /dev/sda; echo 'Resizing the C Drive to 235GiB'; echo '#############################################'; parted /dev/sda resizepart 3 235GiB; ntfsresize --force --force /dev/sda3" ocs_live_extra_param="" ocs_live_batch="no" vga=788 ip= net.ifnames=0  nosplash i915.blacklist=yes radeonhd.blacklist=yes nouveau.blacklist=yes vmwgfx.enable_fbdev=1
  $initrd_cmd /live/initrd.img
}

