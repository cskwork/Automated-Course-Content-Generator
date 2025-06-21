#!/usr/bin/env python3
"""
GPU 확인 스크립트
"""
try:
    import torch
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Device count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    else:
        print("No CUDA devices found")
except Exception as e:
    print(f"Error checking GPU: {e}") 