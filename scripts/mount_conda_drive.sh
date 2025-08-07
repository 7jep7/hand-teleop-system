#!/bin/bash
# Mount the conda environments partition
echo "🔗 Mounting conda environments partition..."

# Check if already mounted
if mountpoint -q /mnt/nvme0n1p8; then
    echo "✅ Partition already mounted at /mnt/nvme0n1p8"
else
    echo "🔧 Mounting /dev/nvme0n1p8..."
    sudo mount -t ntfs /dev/nvme0n1p8 /mnt/nvme0n1p8
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully mounted conda environments partition"
        echo "📁 Available environments:"
        ls -la /mnt/nvme0n1p8/conda-envs/ 2>/dev/null || echo "   (No conda-envs directory found)"
    else
        echo "❌ Failed to mount partition"
        exit 1
    fi
fi

echo "🐍 Conda environments location: /mnt/nvme0n1p8/conda-envs/"
echo "🚀 You can now use: source /mnt/nvme0n1p8/conda-envs/hand-teleop/bin/activate"
