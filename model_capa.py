import timm
m = timm.create_model('vit_base_patch16_224.augreg_in1k', pretrained=False)
n = sum(v.numel() for v in m.state_dict().values())
print("# params : ", n)
print(f'{n*4/1024**2:.1f} MiB (fp32)')